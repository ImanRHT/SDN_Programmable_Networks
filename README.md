# SDN_Programmable_Networks
This repository contain essential networking functionalities—TCP/UDP protocols and ACLs—using the P4 programming language.

### Getting Started  

#### Step 1: Set Up the Environment  

1. **Install VirtualBox**  
   Ensure you have VirtualBox installed on your system.  

2. **Download the Virtual Machine (VM)**  
   Get the pre-configured VM from the INL Lab:  
   - **Username:** `p4`  
   - **Password:** `p4`  

3. **Clone this Repository**  
   Use the following commands to clone the project repository and navigate to the project directory:  
   ```bash  
   git clone https://github.com/your-repo.git  
   cd your-repo  
   cd course-net/spring2021-1/assignment2  

4. **Explore Resources**
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
