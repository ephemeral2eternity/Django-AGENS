import urllib.parse
import socket
import time
import ntpath
import json
import os
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template import RequestContext, loader
from django.http import HttpResponse
from qoe.qoe_utils import *

# Create your views here.
# The page returned for the request: http://cache_agent_ip:port/overlay/
def index(request):
	return HttpResponse("Please come back later. The site is under construction.")

@csrf_exempt
def initQoE(request):
	initializeQoE()
	return query(request)

@csrf_exempt
def query(request):
	cur_host = str(socket.gethostname())
	qoe_dict = getQoEStr()
	print(qoe_dict)
	templates = loader.get_template('qoe/qoes.html')
	context = RequestContext(request, {
					'localhost' : cur_host,
					'qoes' : qoe_dict,
	})
	return HttpResponse(templates.render(context))

@csrf_exempt
def update(request):
	url = request.get_full_path()
	params = url.split('?')[1]
	update_dict = urllib.parse.parse_qs(params)
	print(update_dict)
	if 'srv' in update_dict.keys():
		srv = update_dict['srv'][0]
		if 'qoe' in update_dict.keys():
			qoe = float(update_dict['qoe'][0])
			if 'alpha' in update_dict.keys():
				alpha = float(update_dict['alpha'][0])
			else:
				alpha = 0.1
			updateQoE(srv, qoe, alpha)
		else:
			print('QoE update message needs to denote the qoe in request ', params)
			raise Http404
	else:
		print('QoE update message needs to denote the server name in request ', params)
		raise Http404
	return HttpResponse('Successfully update QoE value!')

@csrf_exempt
def dump(request):
	## Dump the qoe objects
	all_qoe = QoE.objects.all()
	qoes = {}
	qoes_id = {}

	for qoe_obj in all_qoe:
		if qoe_obj.srv not in qoes.keys():
			qoes[qoe_obj.srv] = {}
		cur_ts = int(time.mktime(qoe_obj.time.timetuple()))
		qoes[qoe_obj.srv][cur_ts] = float(qoe_obj.qoe)
		qoes_id[qoe_obj.srv] = int(qoe_obj.id)

	cur_file_path = os.path.realpath(__file__)
	cur_path, cur_file_name = ntpath.split(cur_file_path)
	cur_host_name = str(socket.gethostname())
	ts = time.strftime('%m%d%H%M')
	qoes_file = cur_path + '/tmp/' + cur_host_name + '_' + ts + '_QoE.json'

	with open(qoes_file, 'w') as outfile:
		json.dump(qoes, outfile, sort_keys=True, indent=4, ensure_ascii=False)

	gcs_upload('agens-data', qoes_file)

	for qoe_obj in all_qoe:
		if int(qoe_obj.id) < qoes_id[qoe_obj.srv] - 10:
			qoe_obj.delete()

	return HttpResponse("Dump QoE files successfully to gs://agens-data/ with timestamp " + ts + "!!!!")
