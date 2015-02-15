import json
import socket
import re
import subprocess

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
