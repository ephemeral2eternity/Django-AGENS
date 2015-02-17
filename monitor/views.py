import os
import ntpath
import socket
import time
import json
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template import RequestContext, loader
from django.http import HttpResponse
from monitor.models import Load, BW
from monitor.gcs_upload import *

# Create your views here.
def index(request):
	return HttpResponse("Please come back later!")

# Create videos for recent load request
@csrf_exempt
def view_load(request):
	load_list = Load.objects.order_by('-pk')[:30]
	template = loader.get_template('monitor/load.html')
	context = RequestContext(request, {
					'load_list':load_list,
	})
	return HttpResponse(template.render(context))

@csrf_exempt
def view_bw(request):
	bw_list = BW.objects.order_by('-pk')[:30]
	template = loader.get_template('monitor/bw.html')
	context = RequestContext(request, {
					'bw_list':bw_list,
	})
	return HttpResponse(template.render(context))

@csrf_exempt
def dump(request):
	## Dump the load objects
	all_load = Load.objects.all()
	load_cnt = all_load.count()
	all_bw = BW.objects.all()
	bw_cnt = all_bw.count()

	# export load objects to json file and only leave the most 10 recent objects
	load = {}
	n = 0
	for load_obj in all_load:
		cur_ts = int(time.mktime(load_obj.time.timetuple()))
		load[cur_ts] = int(load_obj.load)
		if n < load_cnt - 10:
			load_obj.delete()
		n = n + 1

	# export bw objects to json file and only leave the most 10 recent objects
	bw = {}
	n = 0
	for bw_obj in all_bw:
		cur_ts = int(time.mktime(bw_obj.time.timetuple()))
		bw[cur_ts] = float(bw_obj.bw)
		if n < bw_cnt - 10:
			bw_obj.delete()
		n = n + 1

	cur_file_path = os.path.realpath(__file__)
	cur_path, cur_file_name = ntpath.split(cur_file_path)
	cur_host_name = str(socket.gethostname())
	ts = time.strftime('%m%d%H%M')
	load_file = cur_path + '/tmp/' + cur_host_name + '_' + ts + '_load.json'
	bw_file = cur_path + '/tmp/' + cur_host_name + '_' + ts + '_bw.json'

	with open(load_file, 'w') as outfile:
		json.dump(load, outfile, sort_keys=True, indent=4, ensure_ascii=False)

	with open(bw_file, 'w') as outfile:
		json.dump(bw, outfile, sort_keys=True, indent=4, ensure_ascii=False)

	gcs_upload('agens-data', load_file)
	gcs_upload('agens-data', bw_file)
	return HttpResponse("Dump Load and BW files successfully to gs://agens-data/ with timestamp " + str(ts) + "!!!")
