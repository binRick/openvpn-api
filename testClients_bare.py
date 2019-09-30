#!/usr/bin/env python3
import time, json, openvpn_api.vpn

SERVERS = {
  'udp': {
    'sock': '/root/openvpn-management-udp.sock',
  },
  'tcp': {
    'sock': '/root/openvpn-management-tcp.sock',
  },
}

def extractClientConnections():
    CLIENT_CONNECTIONS = []
    for PROTO in SERVERS.keys():
        O = openvpn_api.VPN(socket=SERVERS[PROTO]['sock'])
        with O.connection():
            SERVER_CONNECTIONS = O.connected_clients()
            for C in SERVER_CONNECTIONS:
                C['proto'] = PROTO
                CLIENT_CONNECTIONS.append(C)
    return CLIENT_CONNECTIONS


print(json.dumps(extractClientConnections()))
