from operator import attrgetter
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet, ether_types
from ryu.topology.api import get_switch, get_link, get_host
from ryu.topology import event
import networkx as nx
import matplotlib.pyplot as plt
from ryu.lib import hub
import random

class ExampleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ExampleSwitch13, self).__init__(*args, **kwargs)
        self.net = nx.Graph()
        # initialize potential hosts and their corresponding port & datapath
        self.host_ports = {}
        # initialize list of datapaths.
        self.datapaths = []
        # initialize required config variables
        self.HARD_TIMEOUT = 10
        # ======================== IMPORTANT ======================== 
        # first I implemented this link monitoring system but later I figured out that it's 
        # useless for my current algorithm, so I disabled it.
        # ======================== IMPORTANT ======================== 

        # initialize link monitoring system
        # self.SLEEP = 10
        # self.LINK_CAP = 100
        # self.utilization_thread = hub.spawn(self.link_utilization)

    # this function periodically send stat request to obtain monitoring information
    def link_utilization(self):
        while 1:
            for datapath in self.datapaths:
                ofproto = datapath.ofproto
                parser = datapath.ofproto_parser

                req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
                datapath.send_msg(req)
            hub.sleep(self.SLEEP)

    # this function gather information about transferred rate from any ports in corresponding datapath
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        for port_stat in body:
            tx_bytes = port_stat.tx_bytes
            tx_bytes /= 1024
            tx_bytes /= 1024

            for key in self.net[ev.msg.datapath.id]:
                if 'weight' in self.net[ev.msg.datapath.id][key] and \
                    self.net[ev.msg.datapath.id][key]['port'] == port_stat.port_no:
                    edge = self.net[ev.msg.datapath.id][key]
                    utilization = (tx_bytes - edge['old_Mbytes']) / (self.LINK_CAP * self.SLEEP)
                    self.net[ev.msg.datapath.id][key]['weight'] = abs(int((1.0 - utilization) * 100))
                    self.net[ev.msg.datapath.id][key]['old_Mbytes'] = tx_bytes
                    print(ev.msg.datapath.id, key, tx_bytes, abs(int((1.0 - utilization) * 100)))
                    break

    # install the table-miss flow entry.
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, 0, match, actions)

    # add given flow to specific switch.
    def add_flow(self, datapath, priority, hard_timeout, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst,
            hard_timeout=hard_timeout)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # get src and dst mac addresses.
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src
        if eth_pkt.ethertype == ether_types.ETH_TYPE_LLDP or eth_pkt.ethertype == ether_types.ETH_TYPE_IPV6:
            return 

        # get the received port number from packet_in message.
        in_port = msg.match['in_port']
        # get datapah id of this packet
        dpid = datapath.id

        # check if mac address isn't available learn it
        if src not in self.net:
            self.net.add_node(src)
            self.net.add_edges_from([(src, dpid)])
            self.net.add_edges_from([(dpid, src, {'port': in_port, 'weight': 100, 'old_Mbytes': 0.0})])

        # in case of ARP packet route the packet correspondingly
        # we will send this packet to all hosts
        if eth_pkt.ethertype == ether_types.ETH_TYPE_ARP:
            out_port_set = set()
            i = 1
            for key in self.host_ports:
                for _ in self.host_ports[key]:
                    calculated_path = nx.shortest_path(self.net, src, 'h' + str(i), weight='weight')
                    i += 1
                    try:
                        next_hop = calculated_path[calculated_path.index(dpid) + 1]
                    except:
                        continue
                    out_port = self.net[dpid][next_hop]['port']
                    if in_port == out_port:
                        continue
                    out_port_set.add(out_port)

            # after selecting all port which this packet should be forwarded to 
            # we construct the corresponding message for doing this.
            actions = []
            for out_port in out_port_set:
                actions.append(parser.OFPActionOutput(out_port))
            out = parser.OFPPacketOut(datapath=datapath,
                    buffer_id=ofproto.OFP_NO_BUFFER,
                    in_port=in_port, actions=actions,
                    data=msg.data)
            datapath.send_msg(out)
            return

        # obtain all shortest paths, then select one of them based on their (src + dst) hash
        calculated_paths = list(nx.all_shortest_paths(self.net, src, dst))
        rand = hash(src + dst)
        calculated_path = calculated_paths[rand % len(calculated_paths)]
        next_hop = calculated_path[calculated_path.index(dpid) + 1]
        out_port = self.net[dpid][next_hop]['port']

        # add corresponding flow rule.
        actions = [parser.OFPActionOutput(out_port)]
        match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
        self.add_flow(datapath, 1, self.HARD_TIMEOUT, match, actions)

        # construct packet_out message and send it.
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=in_port, actions=actions,
                                  data=msg.data)
        datapath.send_msg(out)

    @set_ev_cls(event.EventSwitchEnter)
    def enter_switch_handler(self, ev):
        self.get_topology_data(ev)

    @set_ev_cls(event.EventSwitchLeave)
    def leave_switch_handler(self, ev):
        self.get_topology_data(ev)

    @set_ev_cls(event.EventLinkAdd)
    def host_handler(self, ev):
        self.get_topology_data(ev)

    @set_ev_cls(event.EventLinkDelete)
    def host_handler(self, ev):
        self.get_topology_data(ev)

    def get_topology_data(self, ev):
        self.net = nx.DiGraph()
        self.host_ports = {}
        datapath_list = get_switch(self, None)
        self.datapaths = []
        datapaths = []
        # adding datapaths to our network graph
        for dp in datapath_list:
            self.host_ports[dp.dp.id] = [port.port_no for port in dp.ports]
            self.datapaths.append(dp.dp)
            datapaths.append(dp.dp.id)
        self.net.add_nodes_from(datapaths)

        # adding links to our network graph as edges
        links_list = get_link(self, None)
        links = []
        for link in links_list:
            self.host_ports[link.src.dpid].remove(link.src.port_no)
            if len(self.host_ports[link.src.dpid]) == 0:
                del self.host_ports[link.src.dpid]
            links.append((link.src.dpid, link.dst.dpid, {'weight': 100, 'port': link.src.port_no, 'old_Mbytes': 0.0}))
        self.net.add_edges_from(links)

        # find unused links, as they are probably our candidate hosts
        i = 1
        for key in self.host_ports:
            for value in self.host_ports[key]:
                self.net.add_node('h' + str(i))
                self.net.add_edges_from([('h' + str(i), key)])
                self.net.add_edges_from([(key, 'h' + str(i), {'port': value, 'weight': 100, 'old_Mbytes': 0.0})])
                i += 1
