#!/usr/bin/env python3
import os, sys, socket, json
import openvpn_api.vpn

SERVERS = {
  'udp': '/root/openvpn-management-udp.sock',
  'tcp': '/root/openvpn-management-tcp.sock',
}

for PROTO in SERVERS.keys():
	O = openvpn_api.VPN(socket=SERVERS[PROTO])
	with O.connection():
		S = O.get_status()
		s = O.get_stats()
		print("OpenVPN")
		print("  Protocol: {}".format(PROTO))
		print("  Version: {}".format(O.version))
		print("  Release: {}".format(O.release))
		print("  Running Since: {}".format(O.state.up_since))
		print("  State: {}".format(O.state.state_name))
		print("  Local Address: {}".format(O.state.local_virtual_v4_addr))
		print("  Bytes: {} sent / {} recv".format(s.bytes_out, s.bytes_in))
		print("  Connected Clients: {}".format(s.client_count))
		print("\n")
		print("  Clients".format(len(S.client_list)))
		for _C in S.client_list:
			C = S.client_list[_C]
			print("   [{}]".format(C.common_name))
			print("    CN: {}".format(C.common_name))
			print("    Remote: {}".format(C.real_address))
			print("    Bytes: {} sent / {} recv".format(C.bytes_received, C.bytes_sent))
			print("    Connected Since: {}".format(C.connected_since))
		print("  Routes".format(len(S.routing_table)))
		for _R in S.routing_table:
			R = S.routing_table[_R]
			print("   [{}]".format(R.common_name))
			print("    CN: {}".format(R.common_name))
			print("    Remote: {}".format(R.real_address))
			print("    Local: {}".format(R.virtual_address))
			print("    Last Update: {}".format(R.real_address))
		print("\n")
