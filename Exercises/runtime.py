import argparse, os, sys, grpc

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../utils/'))

import p4runtime_lib.bmv2, p4runtime_lib.helper
from p4runtime_lib.switch import ShutdownAllSwitchConnections

p4info = './build/acl_tunnel.p4.p4info.txt'
bmv2_json = './build/acl_tunnel.json'


p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info)
sw = p4runtime_lib.bmv2.Bmv2SwitchConnection(
    name='s3', address='127.0.0.1:50053', device_id=2, proto_dump_file='logs/s3-p4runtime-requests.txt')
sw.MasterArbitrationUpdate()
#sw.SetForwardingPipelineConfig(p4info=p4info_helper.p4info, bmv2_json_file_path=bmv2_json)

parser = argparse.ArgumentParser(description='P4Runtime Controller')
parser.add_argument('--udp_port', type=int, required=False)
parser.add_argument('--dst_ip', type=str, required=False)
args = parser.parse_args()

udp_port = args.udp_port
dst_ip = args.dst_ip

match_fields = {}
if udp_port != None:
    match_fields["hdr.udp.dstPort"] = [udp_port, 65535]
if dst_ip != None:
    match_fields["hdr.ipv4.dstAddr"] = [dst_ip, 4294967295]
assert len(match_fields)>0

table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.access_control",
            match_fields=match_fields,
            action_name="MyIngress.drop",
            action_params={},
            priority=1
            )
sw.WriteTableEntry(table_entry)
print('entry added to flow table of switch s3')
ShutdownAllSwitchConnections()
