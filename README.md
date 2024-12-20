# SDN_Programmable_Networks
This repository contain essential networking functionalities—TCP/UDP protocols and ACLs—using the P4 programming language.

### Getting Started  

#### Step 1: Set Up the Environment  

1. **Install VirtualBox**  
   Ensure you have VirtualBox installed on your system.  

2. **Clone this Repository**  
   Use the following commands to clone the project repository and navigate to the project directory:  
   ```bash  
   git clone https://github.com/your-repo.git  
   cd your-repo  
   cd course-net/spring2021-1/assignment2  

3. **Explore Resources**
   Utilize the P4 tutorial and cheatsheet as valuable references throughout the development process.


## TCP and UDP Implementation  
Develop a P4 program to implement the functionality of the TCP and UDP transport layer protocols on a switch.  



let's compile the incomplete `acl.p4` and bring up a switch in Mininet to test its behavior.

1. In your shell, run:
   ```bash
   make run
   ```
   This will:
   * compile `acl.p4`, and
   * start a Mininet instance with one switch (`s1`) connected to four hosts (`h1`, `h2`, `h3` and `h4`). Mininet is a network simulator that can simulate a virtual network in the VM.
   * The hosts are assigned with IP addresses of `10.0.1.1`, `10.0.1.2`, `10.0.1.3` and `10.0.1.4`.
   The output of this command line may be useful when you debug.

2. You should now see a Mininet command prompt. Open two terminals
for `h1` and `h2`, respectively:
   ```bash
   mininet> xterm h1 h2
   ```
3. Each host includes a small Python-based messaging client and
server. In `h2`'s xterm, go to the current exercise folder (`cd exercises/acl`) and start the server with the listening port:
   ```bash
   ./receive.py 80
   ```
4. In `h1`'s xterm, go to the current exercise folder (`cd exercises/acl`) and send a message to `h2`:
   ```bash
   ./send.py 10.0.1.2 UDP 80 "P4 IS COOL"
   ```
   The command line means `h1` will send a message to `10.0.1.2` with udp.dstport=80.
   The message will **not** be received and displayed in `h2`.

   A P4 program defines a packet-processing pipeline, but the rules
   within each table are inserted by the control plane. When a rule
   matches a packet, its action is invoked with parameters supplied by
   the control plane as part of the rule.

   As part of bringing up the Mininet instance, the
   `make run` command will install packet-processing rules in the tables of
   each switch. These are defined in the `s1-acl.json` files.

   **Important:** We use P4Runtime to install the control plane rules. The
   content of files `s1-acl.json` refer to specific names of tables, keys, and
   actions, as defined in the P4Info file produced by the compiler (look for the
   file `build/acl.p4info` after executing `make run`). Any changes in the P4
   program that add or rename tables, keys, or actions will need to be reflected in
   these `s1-acl.json` files.


## Access Control List (ACL)  
Create a P4 program to enforce an ACL on a switch, allowing or blocking network traffic based on predefined rules.  

<!-- The `acl.p4` file contains a skeleton P4 program with key pieces of
logic replaced by `TODO` comments. Your implementation should follow
the structure given in this file---replace each `TODO` with logic
implementing the missing piece. -->

A complete `acl.p4` will contain the following components:

1. Header type definitions for Ethernet (`ethernet_t`), IPv4 (`ipv4_t`), TCP (`tcp_t`) and UDP (`udp_t`).
2. Parsers for Ethernet, IPv4, TCP or UDP headers.
3. An action `drop()` to drop a packet, using `mark_to_drop()`.
4. An action (called `ipv4_forward`) that:
	1. Sets the egress port for the next hop.
	2. Updates the ethernet destination address with the address of the next hop.
	3. Updates the ethernet source address with the address of the switch.
	4. Decrements the TTL.
5. A control that:
    1. Defines a table that will match IP dstAddr and UDP dstPort, and
       invoke either `drop` or `NoAction`.
    2. An `apply` block that applies the table.
    3. Rules added to `s1-acl.json` that denies all the UDP packets with dstPort=80 or dstAddr=10.0.1.4.  
6. A `package` instantiation supplied with the parser, control, and deparser.
    > In general, a package also requires instances of checksum verification
    > and recomputation controls. These are not necessary for this assignment
    > and are replaced with instantiations of empty controls.




## Obtaining required software

1. Follow the instructions in [P4 lang tutorials](https://github.com/p4lang/tutorials) and install the required VM.
2. install `iperf3` on the VM.

  ```bash
    sudo apt-get install iperf3
  ```
3. On the VM, cloen this repository

```bash
    git clone -b spring-2022 https://github.com/arshiarezaei/course-net.git
  ```

## Step 1: Implement Tunneling

A complete implementation of the `basic_tunnel.p4` switch will be able to forward based on the contents of a custom encapsulation header as well as perform normal IP forwarding if the encapsulation header does not exist in the packet.


1. **NOTE:** A new header type has been added called `myTunnel_t` that contains
two 16-bit fields: `proto_id` and `dst_id`.
2. **NOTE:** The `myTunnel_t` header has been added to the `headers` struct.

## Step 2: Implement ACL for the Switch `s3`

In the switch `s3` you must also add a simple access control list (ACL) that simply drops every packet with `UDP destination port == 80` and `ipv4 dstAddress==10.0.3.3`.

**Important: if you hard code ACL roles in the data plane you lose some points.**

### Step 3: Add Forwarding Table Enteries

A P4 program defines a packet-processing pipeline, but the rules within each table are inserted by the control plane. When a rule matches a packet, its action is invoked with parameters supplied by the control plane as part of the rule.

For this exercise, you have to added the necessary rules to `sX-runtime.json`.


**Important: You will be asked to modify the forwarding behavior of the control plane.**


## Step 3: Run your solution

1. In your shell, run:
   ```bash
   make run
   ```
   This will:
   * compile `tunnel.p4` and `acl_tunnel.p4`
   * start a Mininet instance with three switches (`s1`, `s2`, `s3`) configured
     in a triangle, each connected to one host (`h1`, `h2`, and `h3`).
   * The hosts are assigned IPs of `10.0.1.1`, `10.0.2.2`, and `10.0.3.3`.

2. You should now see a Mininet command prompt. Open two terminals for `h1` and
`h2`, respectively:

  ```bash
  mininet> xterm h1 h2
  ```
3. Each host includes a small Python-based messaging client and server. In
`h2`'s xterm, start the server:

  ```bash
  ./receive.py
  ```
4. First we will test without tunneling. In `h1`'s xterm, send a message to`h2`:

  ```bash
  ./send.py 10.0.2.2 "P4 is cool"
  ```
  The packet should be received at `h2`. If you examine the received packet
  you should see that is consists of an Ethernet header, an IP header, a TCP
  header, and the message. If you change the destination IP address (e.g. try
  to send to `10.0.3.3`) then the message should not be received by `h2`, and
  will instead be received by `h3`.
  
5. Type `exit` or `Ctrl-D` to leave each xterm and the Mininet command line.


#### Cleaning up Mininet

In the latter two cases above, `make` may leave a Mininet instance running in
the background. Use the following command to clean up these instances:

```bash
make stop
```

### Policy

If you violate any of the following rules, you will get `0` for this assignment.

    1.You must complete this assignment individually.
    2.You are not allowed to share your code (or a peace of it) with other students.
    3.If you use code on the internet you should cite the source(s).


## Submission
You must submit:

* Your source code for the exercises, in a folder called `P4-assignment`  and submit an `assignment2.zip` file. Make sure to submit both the p4 code and the corresponding json file that configures the table entries.

