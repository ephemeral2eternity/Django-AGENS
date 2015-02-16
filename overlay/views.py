import re
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template import RequestContext, loader
from django.http import HttpResponse
from overlay.models import Server, Peer
from overlay.overlay_utils import *
from overlay.ping import *

# Create your views here.
# The page returned for the request: http://cache_agent_ip:port/overlay/
def index(request):
	return HttpResponse("Please come back later. The site is under construction!")

@csrf_exempt
def initServer(request):
	# Delete all objects in the table first
	existing_srvs = Server.objects.all()
	if existing_srvs.count() > 0:
		existing_srvs.delete()
	cache_srv_ips = get_cache_agent_ips()
	hostname = get_host_name()
	print("Obtained cache_srv_ips are", cache_srv_ips)
	print("Current host name is :", hostname)
	for srv in cache_srv_ips.keys():
		srv_id = int(re.findall(r'\d+', srv)[0])
		srv_name = srv
		srv_ip = cache_srv_ips[srv]
		srv_rtt = getMnRTT(srv_ip, 5)
		isLocal = (srv == hostname)
		if isLocal:
			srv_rtt = 0.0
		# print("Is ", srv, " the localhost? ", isLocal)
		cur_srv = Server(id=srv_id, name=srv_name, ip=srv_ip, isLocal=isLocal, rtt=srv_rtt)
		cur_srv.save()
		print(srv_name, " is saved in the database!")

	# Delete all objects in the table Peer
	existing_peers = Peer.objects.all()
	if existing_peers.count() > 0:
		existing_peers.delete()
	connect_overlay()
	
	return query(request)

@csrf_exempt
def query(request):
	# Return the initialized servers
	srv_list = Server.objects.all()
	cur_srv = Server.objects.filter(isLocal=True)
	peer_list = Peer.objects.all()
	# print("The current host is:", cur_srv[0].name)
	templates = loader.get_template('overlay/servers.html')
	context = RequestContext(request, {
					'curSrv' : cur_srv[0],
					'srvs' : srv_list,
					'peers' : peer_list,
	})
	return HttpResponse(templates.render(context))

@csrf_exempt
def update(request):
	url = request.get_full_path()
	params = url.split('?')[1]
	update_dict = url.parse.parse_qs(params)
	if 'srv' in update_dict.keys():
		srv = update_dict['srv'][0]
		srv_obj = Server.objects.filter(name=srv)[0]
		if 'bw' in update_dict.keys():
			srv_obj.bw = float(update_dict['bw'][0])
		elif 'load' in update_dict.keys():
			srv_obj.load = int(update_dict['load'][0])
		else:
			print('Unrecognized update parameters in ', params)
		srv_obj.save()
	else:
		print('Update messages needs to denote the server name in ', params)
	return HttpResponse('Successfully update monitored value in overlay table!')

@csrf_exempt
def peer(request):
	# Answer the peer request from an node
	if request.method == "POST":
		print("overlay/peer request:", request.POST)
		print("overlay/peer request keys:", request.POST.keys())
		peer_node = request.POST.get("node", "")
		print("node info in request:", peer_node)
		peer_id  = int(re.findall(r'\d+', peer_node)[0])
		peer_ip = request.POST.get("ip", "")
		print("ip info in request:", peer_ip)
		new_peer = Peer(id=peer_id, name=peer_node, ip=peer_ip)
		new_peer.save()
		return HttpResponse("Successfully peering with agent " + get_host_name() + ".")
	elif request.method == "GET":
		print("The requested url is: ", request.get_full_path())
		return HttpResponse("Please use POST method to peer with an agent when using http://cache_agent:port/overlay/peer/.")	
