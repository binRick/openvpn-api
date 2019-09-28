#!/usr/bin/env python3
import os, sys, socket, json, psutil, subprocess, humanize, datetime
import openvpn_api.vpn

EXTRACT_CONFIG_KEYS = ['dev','ca','key','cert','max-clients','tls-auth','dh']
SERVERS = {
  'udp': {
	'sock': '/root/openvpn-management-udp.sock',
	'pid': None,
	'log': None,
	'config': None,
	'open_files': [],
	'connections': [],
	'listens': [],

  },
  'tcp': {
	'sock': '/root/openvpn-management-tcp.sock',
	'pid': None,
	'log': None,
	'config': None,
	'open_files': [],
	'connections': [],
	'listens': [],
  },
}

def displayServers():
	for PROTO in SERVERS.keys():
		print("OpenVPN")
		print("  Protocol: {}".format(PROTO))
		print("  PID: {}".format("{}".format(SERVERS[PROTO]['pid'])))
		print("  Started: {}".format(humanize.naturaldate(SERVERS[PROTO]['state'].up_since)))
		print("  Listening on: {}".format(SERVERS[PROTO]['listens']))
		print("  Interface: {}".format("{}".format(SERVERS[PROTO]['dev'])))
		print("  Connections: {}".format("{}".format(SERVERS[PROTO]['connections'])))
		print("  exe: {}".format("{}".format(SERVERS[PROTO]['exe'])))
		print("  User: {}".format("{}".format(SERVERS[PROTO]['user'])))
		print("  Log: {}".format("{}".format(SERVERS[PROTO]['log'])))
		print("  CA: {}".format("{}".format(SERVERS[PROTO]['ca'])))
		print("  Cert: {}".format("{}".format(SERVERS[PROTO]['cert'])))
		print("  Key: {}".format("{}".format(SERVERS[PROTO]['key'])))
		print("  Memory (rss): {}".format("{}".format(humanize.naturalsize(SERVERS[PROTO]['memory_full_info'].rss))))
		print("  cpu_percent: {}".format("{}".format(SERVERS[PROTO]['cpu_percent'])))
		print("  # Threads: {}".format("{}".format(SERVERS[PROTO]['num_threads'])))
		print("  # FDs: {}".format("{}".format(SERVERS[PROTO]['num_fds'])))
		print("  Max Clients: {}".format("{}".format(SERVERS[PROTO]['max-clients'])))
		print("  Mgmt Socket: {}".format("{}".format(SERVERS[PROTO]['sock'])))
		print("  Config: {}".format("{}".format(SERVERS[PROTO]['config'])))
		print("  Open Files: {}".format("{}".format(SERVERS[PROTO]['open_files'])))
		print("  Version: {}".format(SERVERS[PROTO]['version']))
		print("  Release: {}".format(SERVERS[PROTO]['release']))
		print("  State: {}".format(SERVERS[PROTO]['state'].state_name))
		print("  Local Address: {}".format(SERVERS[PROTO]['state'].local_virtual_v4_addr))
		print("  Bytes: {} sent / {} recv".format(SERVERS[PROTO]['stats'].bytes_out, SERVERS[PROTO]['stats'].bytes_in))
		print("  Connected Clients: {}".format(SERVERS[PROTO]['stats'].client_count))
		if SERVERS[PROTO]['stats'].client_count > 0:
			print("   [Clients]".format(len(SERVERS[PROTO]['status'].client_list)))
			for _C in SERVERS[PROTO]['status'].client_list:
				C = SERVERS[PROTO]['status'].client_list[_C]
				print("    [{}]".format(C.common_name))
				print("     CN: {}".format(C.common_name))
				print("     Remote: {}".format(C.real_address))
				print("     Bytes: {} sent / {} recv".format(C.bytes_received, C.bytes_sent))
				print("     Connected Since: {}".format(C.connected_since))
			print("   [Routes]".format(len(SERVERS[PROTO]['status'].routing_table)))
			for _R in SERVERS[PROTO]['status'].routing_table:
				R = SERVERS[PROTO]['status'].routing_table[_R]
				print("    [{}]".format(R.common_name))
				print("     CN: {}".format(R.common_name))
				print("     Remote: {}".format(R.real_address))
				print("     Local: {}".format(R.virtual_address))
				print("     Last Update: {}".format(R.real_address))
			print("\n")


def parseServers():
	for PROTO in SERVERS.keys():
		for k in EXTRACT_CONFIG_KEYS:
			SERVERS[PROTO][k] = None
		O = openvpn_api.VPN(socket=SERVERS[PROTO]['sock'])
		with O.connection():
			SERVERS[PROTO]['status'] = O.get_status()
			SERVERS[PROTO]['stats'] = O.get_stats()
			SERVERS[PROTO]['state'] = O.state
			SERVERS[PROTO]['version'] = O.version
			SERVERS[PROTO]['release'] = O.release
			child = subprocess.Popen(["lsof","-t",SERVERS[PROTO]['sock']], stdout=subprocess.PIPE)
			pids, err = child.communicate()
			exit_code = child.returncode
			if exit_code != 0:
				raise Exception("[{}] Unable to lsof {}".format(PROTO,SERVERS[PROTO]['sock']))
			pids = pids.decode().strip().split("\n")
			for pid in pids:
				if not SERVERS[PROTO]['config']:
					Process = psutil.Process(int(pid))
					SERVERS[PROTO]['exe'] = Process.exe()
					SERVERS[PROTO]['cmdline'] = Process.cmdline()
					if SERVERS[PROTO]['exe'].endswith("openvpn"):
						SERVERS[PROTO]['pid'] = int(pid)
						for w in SERVERS[PROTO]['cmdline']:
							if w.lower().endswith('.conf'):
								SERVERS[PROTO]['config'] = w
						SERVERS[PROTO]['user'] = Process.username()
						SERVERS[PROTO]['num_threads'] = Process.num_threads()
						SERVERS[PROTO]['cpu_percent'] = Process.cpu_percent()
						SERVERS[PROTO]['num_fds'] = Process.num_fds()
						SERVERS[PROTO]['_connections'] = Process.connections()
						SERVERS[PROTO]['memory_full_info'] = Process.memory_full_info()
						for of in Process.open_files():
							SERVERS[PROTO]['open_files'].append(of.path)
							if of.path.lower().endswith('.log'):
								SERVERS[PROTO]['log'] = of.path
			if not SERVERS[PROTO]['_connections']:
				raise Exception("[{}] Unable to find connections".format(PROTO))
			for c in SERVERS[PROTO]['_connections']:
				if int("{}".format(c.type)) == 2:
					if c.status == 'NONE':
						SERVERS[PROTO]['listens'].append("{}:{}".format(c.laddr.ip,c.laddr.port))
				elif int("{}".format(c.type)) == 1:
					if c.status == 'ESTABLISHED':
						SERVERS[PROTO]['connections'].append({
							"local": "{}:{}".format(c.laddr.ip,c.laddr.port),
							"remote": "{}:{}".format(c.raddr.ip,c.raddr.port),
						})
					elif c.status == 'LISTEN':
						SERVERS[PROTO]['listens'].append("{}:{}".format(c.laddr.ip,c.laddr.port))
				
			if not SERVERS[PROTO]['config'] or not os.path.exists(SERVERS[PROTO]['config']):
				raise Exception("[{}] Cannot read config {}".format(PROTO, SERVERS[PROTO]['config']))
			with open(SERVERS[PROTO]['config'],'r') as f:
				for l in f.read().strip().splitlines():
					words = ' '.join(l.strip().split(' ')).split()
					for k in EXTRACT_CONFIG_KEYS:
						if words and len(words) == 2 and words[0] == k:
							SERVERS[PROTO][k] = words[1]
			if not SERVERS[PROTO]['dev'] in psutil.net_if_addrs().keys():
				raise Exception("[{}] Invalid Interface {}".format(PROTO, SERVERS[PROTO]['dev']))


if __name__ == "__main__":
	parseServers()
	displayServers()
