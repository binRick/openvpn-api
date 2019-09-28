#!/usr/bin/env python3
import os, sys, socket, json, psutil, subprocess
import openvpn_api.vpn

SERVERS = {
  'udp': {
	'sock': '/root/openvpn-management-udp.sock',
	'pid': None,
	'log': None,
	'config': None,
	'connections': [],
	'open_files': [],

  },
  'tcp': {
	'sock': '/root/openvpn-management-tcp.sock',
	'pid': None,
	'log': None,
	'config': None,
	'connections': [],
	'open_files': [],
  },
}

EXTRACT_CONFIG_KEYS = ['dev','ca','key','cert','max-clients','tls-auth','dh']
INTERFACES = psutil.net_if_addrs().keys()

for PROTO in SERVERS.keys():
	for k in EXTRACT_CONFIG_KEYS:
		SERVERS[PROTO][k] = None
	O = openvpn_api.VPN(socket=SERVERS[PROTO]['sock'])
	pids, err = subprocess.Popen(["lsof","-t",SERVERS[PROTO]['sock']], stdout=subprocess.PIPE).communicate()
	pids = pids.decode().strip().split("\n")
	for pid in pids:
		if not SERVERS[PROTO]['config']:
			Process = psutil.Process(int(pid))
			SERVERS[PROTO]['exe'] = Process.exe()
			if SERVERS[PROTO]['exe'].endswith("openvpn"):
				SERVERS[PROTO]['pid'] = int(pid)
				SERVERS[PROTO]['cmdline'] = Process.cmdline()
				for w in SERVERS[PROTO]['cmdline']:
					if w.lower().endswith('.conf'):
						SERVERS[PROTO]['config'] = w
				SERVERS[PROTO]['user'] = Process.username()
				for of in Process.open_files():
					SERVERS[PROTO]['open_files'].append(of.path)
					if of.path.lower().endswith('.log'):
						SERVERS[PROTO]['log'] = of.path
	with open(SERVERS[PROTO]['config'],'r') as f:
		for l in f.read().strip().splitlines():
			words = ' '.join(l.strip().split(' ')).split()
			for k in EXTRACT_CONFIG_KEYS:
				if words and len(words) == 2 and words[0] == k:
					SERVERS[PROTO][k] = words[1]

	with O.connection():
		S = O.get_status()
		s = O.get_stats()
		print("OpenVPN")
		print("  Protocol: {}".format(PROTO))
		print("  PID: {}".format("{}".format(SERVERS[PROTO]['pid'])))
		print("  Interface: {}".format("{}".format(SERVERS[PROTO]['dev'])))
		print("  exe: {}".format("{}".format(SERVERS[PROTO]['exe'])))
		print("  User: {}".format("{}".format(SERVERS[PROTO]['user'])))
		print("  Log: {}".format("{}".format(SERVERS[PROTO]['log'])))
		print("  CA: {}".format("{}".format(SERVERS[PROTO]['ca'])))
		print("  Cert: {}".format("{}".format(SERVERS[PROTO]['cert'])))
		print("  Key: {}".format("{}".format(SERVERS[PROTO]['key'])))
		print("  Max Clients: {}".format("{}".format(SERVERS[PROTO]['max-clients'])))
		print("  Mgmt Socket: {}".format("{}".format(SERVERS[PROTO]['sock'])))
		print("  Config: {}".format("{}".format(SERVERS[PROTO]['config'])))
		print("  Open Files: {}".format("{}".format(SERVERS[PROTO]['open_files'])))
		print("  Version: {}".format(O.version))
		print("  Release: {}".format(O.release))
		print("  Running Since: {}".format(O.state.up_since))
		print("  State: {}".format(O.state.state_name))
		print("  Local Address: {}".format(O.state.local_virtual_v4_addr))
		print("  Bytes: {} sent / {} recv".format(s.bytes_out, s.bytes_in))
		print("  Connected Clients: {}".format(s.client_count))
		if s.client_count > 0:
			print("   [Clients]".format(len(S.client_list)))
			for _C in S.client_list:
				C = S.client_list[_C]
				print("    [{}]".format(C.common_name))
				print("     CN: {}".format(C.common_name))
				print("     Remote: {}".format(C.real_address))
				print("     Bytes: {} sent / {} recv".format(C.bytes_received, C.bytes_sent))
				print("     Connected Since: {}".format(C.connected_since))
			print("   [Routes]".format(len(S.routing_table)))
			for _R in S.routing_table:
				R = S.routing_table[_R]
				print("    [{}]".format(R.common_name))
				print("     CN: {}".format(R.common_name))
				print("     Remote: {}".format(R.real_address))
				print("     Local: {}".format(R.virtual_address))
				print("     Last Update: {}".format(R.real_address))
			print("\n")
