import json
import socket
import re
import subprocess
import urllib.request
import urllib.parse
from overlay.models import Server, Peer

def get_cache_agents():
        # List all instances
        proc = subprocess.Popen("gcloud compute instances list", stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        print("All instances:")
        print(out)
        cache_agents = []
        if out:
                lines = out.splitlines()
                instances = lines[1:]
                for node_str in instances:
                        items = re.split('\s+', node_str.decode())
                        if "cache" in items[0]:
                                node = {}
                                node['name'] = str(items[0])
                                node['zone'] = str(items[1])
                                node['type'] = str(items[2])
                                node['ip'] = str(items[4])
                                cache_agents.append(node)

        return cache_agents

def get_cache_agent_names():
	nodes = get_cache_agents()
	agent_names = []
	for node in nodes:
		agent_names.append(node['name'])
	return agent_names

def get_cache_agent_ips():
        cache_agents = get_cache_agents()

        # List all instances
        agent_ips = {}
        for node in cache_agents:
                agent_ips[node['name']] = node['ip']

        return agent_ips

def get_host_name():
	return str(socket.gethostname())

def connect_overlay():
	other_srvs = Server.objects.filter(isLocal=False)
	# Find the closest node to peer with
	to_connect = find_closest(other_srvs)
	if peer_with(to_connect):
		print("Successfull peer with agent: ", to_connect.name)
	else:
		print("Failed to peer with agent: ", to_connect.name)
		#other_srv_list.pop(to_connect)
		#to_connect = find_closest(other_srv_list)
		#print("Retry to peer with agent: ", to_connect.name)
		#peer_with(to_connnect.ip)
		

def find_closest(srvs):
	to_connect = srvs[0]
	if len(srvs) > 1:
		for srv in srvs:
			if srv.rtt < to_connect.rtt:
				to_connect = srv
	return to_connect

def peer_with(peer):
	url = 'http://%s:8615/overlay/peer/'%peer.ip
	cur_srv = Server.objects.filter(isLocal=True)[0]
	peer_data = {}
	peer_data['node'] = cur_srv.name
	peer_data['ip'] = cur_srv.ip
	encoded_peer_data = urllib.parse.urlencode(peer_data)
	data = encoded_peer_data.encode('utf-8')

	try:
		req = urllib.request.Request(url, data)
		rsp = urllib.request.urlopen(req)
		rsp_data = rsp.read()
		print(rsp_data)
		peer_name = peer.name
		peer_id = peer.id
		peer_ip = peer.ip
		new_peer = Peer(id=peer_id, name=peer_name, ip=peer_ip)
		new_peer.save()
		return True
	except:
		return False
