#!/usr/bin/env python3
import time, json, openvpn_api.vpn

EXTRACT_CONFIG_KEYS = [] #'dev','ca','key','cert','max-clients','tls-auth','dh']
SERVERS = {
  'udp': {
    'sock': '/root/openvpn-management-udp.sock',
  },
  'tcp': {
    'sock': '/root/openvpn-management-tcp.sock',
  },
}

def extractServerInfo():
    for PROTO in SERVERS.keys():
        for k in EXTRACT_CONFIG_KEYS:
            SERVERS[PROTO][k] = None
        O = openvpn_api.VPN(socket=SERVERS[PROTO]['sock'])
        with O.connection():
            SERVERS[PROTO]['stats'] = vars(O.get_stats())
            SERVERS[PROTO]['version'] = O.version
    return SERVERS


def extractClientConnections():
    CLIENT_CONNECTIONS = []
    for PROTO in SERVERS.keys():
        O = openvpn_api.VPN(socket=SERVERS[PROTO]['sock'])
        with O.connection():
            ROUTES = []
            SERVER_STATUS = O.get_status()
            CLIENT_LIST = SERVER_STATUS.client_list
            ROUTING_TABLE = SERVER_STATUS.routing_table
            for _R in ROUTING_TABLE:
                R = ROUTING_TABLE[_R]
                ROUTE = {
                    "virtual_address": "{}".format(R.virtual_address),
                    "remote": {
                        "address": "{}".format(R.real_address).split(":")[0],
                        "port": int("{}".format(R.real_address).split(":")[1]),
                    },
                    "last_ref_human": "{}".format(R.last_ref),
                    "last_ref": int("{}".format(int(R.last_ref.timestamp())))
                }
                ROUTES.append(ROUTE)
            for _C in CLIENT_LIST:
                C = CLIENT_LIST[_C]
                if C.common_name == 'UNDEF':
                    continue
                CLIENT = {
                    "common_name": C.common_name,
                    "remote": {
                        "address": "{}".format(C.real_address).split(":")[0],
                        "port": int("{}".format(C.real_address).split(":")[1]),
                    },
                    "bytes_received": int("{}".format(int(C.bytes_received))),
                    "bytes_sent": int("{}".format(int(C.bytes_sent))),
                    "bytes_received_human": "{}".format(C.bytes_received),
                    "bytes_sent_human": "{}".format(C.bytes_sent),
                    "connected_since": int("{}".format(int(C.connected_since.timestamp()))),
                    "connected_since_human": "{}".format(C.connected_since),
                    "protocol": "{}".format(PROTO),
                }
                for R in ROUTES:
                    if R['remote']['address'] == CLIENT['remote']['address'] and R['remote']['port'] == CLIENT['remote']['port']:
                        CLIENT['virtual_address'] = R['virtual_address']
                        CLIENT['last_ref_human'] = R['last_ref_human']
                        CLIENT['last_ref'] = R['last_ref']

                CLIENT_CONNECTIONS.append(CLIENT)
    return CLIENT_CONNECTIONS


STATES = {
    "INFO": extractServerInfo(),
    "CONNECTIONS": extractClientConnections(),
}


print(json.dumps(STATES))
