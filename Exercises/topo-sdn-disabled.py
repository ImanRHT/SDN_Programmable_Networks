#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.node import Host
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0 = net.addController('c0', RemoteController)
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)
    s6 = net.addSwitch('s6', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)

    info( '*** Add links\n')
    net.addLink(s1, s2, cls=TCLink, bw=100)
    net.addLink(s2, s4, cls=TCLink, bw=100)
    net.addLink(s4, s6, cls=TCLink, bw=100)
    net.addLink(s6, s5, cls=TCLink, bw=100)
    net.addLink(s5, s3, cls=TCLink, bw=100)
    net.addLink(s3, s1, cls=TCLink, bw=100)
    net.addLink(h1, s1, cls=TCLink, bw=100)
    net.addLink(h2, s1, cls=TCLink, bw=100)
    net.addLink(h3, s6, cls=TCLink, bw=100)
    net.addLink(s6, h4, cls=TCLink, bw=100)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    c0.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s5').start([c0])
    net.get('s6').start([c0])
    net.get('s3').start([c0])
    net.get('s4').start([c0])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

