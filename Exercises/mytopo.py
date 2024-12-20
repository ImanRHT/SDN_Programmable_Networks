
from mininet.topo import Topo


class Simple3PktSwitch(Topo):
    """Simple topology example."""

    def __init__(self, **opts):
        """Create custom topo."""

        # Initialize topology
        super(Simple3PktSwitch, self).__init__(**opts)
        #Topo.__init__(self)

        # Add hosts and switches
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        opts = dict(protocols='OpenFlow13')

        # Adding switches
        s1 = self.addSwitch('s1', dpid="0000000000000001")
        s2 = self.addSwitch('s2', dpid="0000000000000002")
        s3 = self.addSwitch('s3', dpid="0000000000000003")
        s4 = self.addSwitch('s4', dpid="0000000000000004")
        s5 = self.addSwitch('s5', dpid="0000000000000005")
        s6 = self.addSwitch('s6', dpid="0000000000000006")

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)

        self.addLink(h3, s6)
        self.addLink(h4, s6)

        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s4)
        self.addLink(s3, s5)
        self.addLink(s4, s6)
        self.addLink(s5, s6)

topos = { 'mytopo': ( lambda:Simple3PktSwitch() ) }

