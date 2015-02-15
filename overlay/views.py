import re
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template import RequestContext, loader
from django.http import HttpResponse
from overlay.models import Server, Peer
from overlay.get_cache_agents import *
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
		srv_rtt = 255.0
		isLocal = (srv == hostname)
		if isLocal:
			srv_rtt = 0.0
		# print("Is ", srv, " the localhost? ", isLocal)
		cur_srv = Server(id=srv_id, name=srv_name, ip=srv_ip, isLocal=isLocal, rtt=srv_rtt)
		cur_srv.save()
		print(srv_name, " is saved in the database!")
	
	return query(request)

@csrf_exempt
def query(request):
	# Return the initialized servers
	srv_list = Server.objects.all()
	cur_srv = Server.objects.filter(isLocal='Yes')
	# print("The current host is:", cur_srv[0].name)
	templates = loader.get_template('overlay/servers.html')
	context = RequestContext(request, {
					'curSrv' : cur_srv[0],
					'srvs' : srv_list,
	})
	return HttpResponse(templates.render(context))
