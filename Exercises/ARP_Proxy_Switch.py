from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.packet import arp






class L2Switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]  
    arp_table = {"10.0.0.1": "00:00:00:00:00:01",
                 "10.0.0.2": "00:00:00:00:00:02",
                 "10.0.0.3": "00:00:00:00:00:03",
                 "10.0.0.4": "00:00:00:00:00:04"
                 }

	
    def __init__(self, *args, **kwargs):
        super(L2Switch, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser

        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]

        data = None
        if msg.buffer_id == ofp.OFP_NO_BUFFER:
             data = msg.data
    	if eth.ethertype == ether_types.ETH_TYPE_ARP:
            a = pkt.get_protocol(arp.arp)
            self.arp_process(datapath, eth, a, in_port)
            return

        out = ofp_parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data = data)
        dp.send_msg(out)
    def arp_process(self, datapath, eth, a, in_port):
        row = arp_table.get(a.dst_ip)
        if row:
            arp_response = packet.Packet()
            arp_response.add_protocol(ethernet.ethernet(ethertype=eth.ethertype,
                                  dst=eth.src, src=row))
            arp_response.add_protocol(arp.arp(opcode=arp.ARP_REPLY,
                                  src_mac=row, src_ip=a.dst_ip,
                                  dst_mac=a.src_mac,
                                  dst_ip=a.src_ip))

            arp_response.serialize()
            actions = []
            actions.append(datapath.ofproto_parser.OFPActionOutput(in_port))
            parser = datapath.ofproto_parser  
            ofproto = datapath.ofproto
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=arp_response)
            datapath.send_msg(out)
            self.logger.info("ARP Response Sended!!!")
