from django.shortcuts import render
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template import RequestContext, loader
from django.http import HttpResponse
import json
import socket
from client.models import PClient, VClient

# Return all the clients that download videos from the current server.
def index(request):
	return HttpResponse("Please use http://cache_agent_ip:8615/client/pclient/ or http://cache_agent_ip:8615/client/vclient/ to get the proximate client ip addresses and video client ip addresses respectively!")

def query(request):
	pclients = PClient.objects.order_by('-last_visit')[:20]
	vclients = VClient.objects.order_by('-last_visit')[:20]
	cur_host = str(socket.gethostname())
	templates = loader.get_template('client/clients.html')
	context = RequestContext(request, {
					'localhost' : cur_host,
					'pclients' : pclients,
					'vclients' : vclients,
	})
	return HttpResponse(templates.render(context))

def pclient(request):
	pclients = PClient.objects.order_by('-last_visit')[:2]
	pclient_ips = {}
	for pc in pclients:
		pclient_ips[pc.name] = pc.ip

	response = HttpResponse(str(pclient_ips))
	response['Params'] = json.dumps(pclient_ips)
	return response

# Create your views here.
def vclient(request):
	vclients = VClient.objects.order_by('-last_visit')[:2]
	vclient_ips = {}
	for vc in vclients:
		vclient_ips[vc.name] = vc.ip

	response = HttpResponse(str(vclient_ips))
	response['Params'] = json.dumps(vclient_ips)
	return response
