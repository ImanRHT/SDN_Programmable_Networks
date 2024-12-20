from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import arp
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
from collections import defaultdict

class Path(object):
    def __init__(self, src, dst, prev, first_port):
        self.src = src
        self.dst = dst
        self.prev = prev
        self.first_port = first_port
	
    def __repr__(self):
        ret = str(self.dst)
        u = self.prev[self.dst]
        while(u != None):
            ret = str(u) + "->" + ret
            u = self.prev[u]
        return ret			
	

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.topology_api_app = self

        self.host_to_switch = {} #map host mac to tuple of (connected_switch_dp, switch_port) 
        self.switches_dp = set()
        self.switch_ports = {}
        self.host_ports = {}
        self.dpid_to_dp = {}
        self.adj = defaultdict(lambda:defaultdict(lambda:None))
        self.weights = defaultdict(lambda:defaultdict(lambda:None))
        
    @set_ev_cls(event.EventSwitchEnter)
    def update_topology(self, ev):
        switches = get_switch(self.topology_api_app, None)
        links = get_link(self.topology_api_app, None)
        for sw in switches:
            self.switches_dp.add(sw.dp)
            self.switch_ports[sw.dp.id] = set()
            self.host_ports[sw.dp.id] = set()
            self.dpid_to_dp[sw.dp.id] = sw.dp
            
        for link in links:
            #print(link)
            self.switch_ports[link.src.dpid].add(link.src.port_no)
            self.switch_ports[link.dst.dpid].add(link.dst.port_no)
            self.adj[link.src.dpid][link.dst.dpid] = (link.src.port_no, link.dst.port_no)
            self.weights[link.src.dpid][link.dst.dpid] = 0

        for sw in switches:
            all_ports = set([port.port_no for port in sw.ports])
            self.host_ports[sw.dp.id] = all_ports.difference(self.switch_ports[sw.dp.id])

        print(self.switch_ports)
        print('---------------')
        print(self.host_ports)
        print('===============')
        

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    
    def flood_on_hosts(self, msg, data):
        for sw_dp in self.switches_dp:
            for host_port in self.host_ports[sw_dp.id]:
                parser = sw_dp.ofproto_parser
                actions = [parser.OFPActionOutput(host_port)]
                out = parser.OFPPacketOut(datapath=sw_dp, buffer_id=msg.buffer_id,
                                actions=actions, data=data, in_port = sw_dp.ofproto.OFPP_CONTROLLER)
                sw_dp.send_msg(out)
                #print("SENT PACKET TO", sw_dp.id, "TO DELIVER ON HOST PORT", host_port)

    def get_path(self, src, dst):
        adj = self.adj

        distance = {}
        previous = {}
        for dpid in self.adj.keys():
            distance[dpid] = float("+inf")
            previous[dpid] = None
        distance[src.id] = 0

        for i in range(len(self.adj.keys())-1):
            for u in adj.keys(): #nested dict
                for v in adj[u].keys():
                    w = self.weights[u][v]
                    if distance[u] + w < distance[v]:
                        distance[v] = distance[u] + w
                        previous[v] = u 

        first_port = None
        v = dst.id
        u = previous[v]
        while u is not None:
            self.weights[u][v] += 1
            if u == src.id:
                first_port = adj[u][v][0]
            v = u
            u = previous[v]
            
        return Path(src.id, dst.id, previous, first_port)

    def install_path(self, path, msg, eth_dst, eth_src, first_sw_in_port):
        #print(path,'(((((((((((((((((((((((((((((')
        #print(self.weights)
        next_sw = path.dst
        cur_sw = path.prev[next_sw]
        datapath = self.dpid_to_dp[next_sw]
        buffer_id = msg.buffer_id if msg.buffer_id == datapath.ofproto.OFP_NO_BUFFER else None
        parser = datapath.ofproto_parser
        actions = [parser.OFPActionOutput(self.host_to_switch[eth_dst][1])]
        match = parser.OFPMatch(in_port=self.adj[cur_sw][next_sw][1] ,eth_dst=eth_dst, eth_src=eth_src)
        self.add_flow(datapath, 1, match, actions, buffer_id)

        while cur_sw is not None:
            datapath = self.dpid_to_dp[cur_sw]
            parser = datapath.ofproto_parser
            actions = [parser.OFPActionOutput(self.adj[cur_sw][next_sw][0])]
            in_port = self.adj[path.prev[cur_sw]][cur_sw][1] if path.prev[cur_sw] is not None else first_sw_in_port
            match = parser.OFPMatch(in_port=in_port ,eth_dst=eth_dst, eth_src=eth_src)
            self.add_flow(datapath, 1, match, actions, buffer_id)
            next_sw = cur_sw
            cur_sw = path.prev[next_sw]
        return actions
    
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)
        #print("FLOW MOD SENT ^^^^^^^^^^^^^^^^^")
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP or eth.ethertype == 34525:
            return
        dst = eth.dst
        src = eth.src

        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        else:
            data = None

        dpid = datapath.id

        #self.logger.info("packet in %s %s %s %s %s", dpid, src, dst, in_port, eth.ethertype)

        self.host_to_switch[src] = (datapath, in_port)

        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            #print("HANDLING ARP PACKET", src, dst, "@@@@@@@@@@@@@@@")
            self.flood_on_hosts(msg, data)
            return

        if dst in self.host_to_switch:
            path = self.get_path(datapath, self.host_to_switch[dst][0])
            actions = self.install_path(path, msg, dst, src, in_port)
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=data)
            datapath.send_msg(out)
            #print("LEARNED")
        else:
            #print(src, dst, "FLOOD")
            self.flood_on_hosts(msg, data)
            return


        
