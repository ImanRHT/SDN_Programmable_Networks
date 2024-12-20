# Assignment 2: Implementing Tunneling with P4

### Due: Tuesday, Jun 21

![photo](topo-2.png)


## Introduction

In this exercise, we will add support for a tunneling to routers. Your job is to change the P4 code to have the switches add the `myTunnel` header to an IP packet upon ingress to the network and then remove the myTunnel header as the packet leaves to the network to an end host. You have to define a new header type to encapsulate the IP packet and modify the switch code, so that it instead decides the destination port using a new tunnel header.
The new header type will contain a protocol ID, which indicates the type of packet being encapsulated, along with a destination ID to be used for routing.


  - **Start early and feel free to ask questions on Github and [CW](https://cw.sharif.edu)**.
  - **You can also stop by [Performance and Dependability Lab (PDL)](http://pdl.ce.sharif.edu/) (Room #815, CE Dep) with prior appointment.**


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
