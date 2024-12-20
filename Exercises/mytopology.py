from mininet.topo import Topo

class MyTopo(Topo):
	def build(self):
		h1=self.addHost('h1', mac='00:00:00:00:00:01', ip="10.0.0.1")
		h2=self.addHost('h2', mac='00:00:00:00:00:02', ip="10.0.0.2")
		h3=self.addHost('h3', mac='00:00:00:00:00:03', ip="10.0.0.3")
		h4=self.addHost('h4', mac='00:00:00:00:00:04', ip="10.0.0.4")
		s1=self.addSwitch('s1')
		s2=self.addSwitch('s2')
		s3=self.addSwitch('s3')
		s4=self.addSwitch('s4')
		s5=self.addSwitch('s5')
		s6=self.addSwitch('s6')
		s7=self.addSwitch('s7')

		self.addLink(h1,s1)
		self.addLink(s1,s2)
		self.addLink(s1,s5)
		self.addLink(s1,s3)
		self.addLink(h3,s3)
		self.addLink(s3,s6)
		self.addLink(s3,s5)
		self.addLink(s2,s4)
		self.addLink(s2,s5)
		self.addLink(h4,s4)
		self.addLink(s5,s4)
		self.addLink(s5,s6)
		self.addLink(s5,s7)
		self.addLink(s4,s7)
		self.addLink(s6,s7)
		self.addLink(s7,h2)
topos={ 'mytopo':( lambda:MyTopo())}
