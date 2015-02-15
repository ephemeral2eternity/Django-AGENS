from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template import RequestContext, loader
from django.http import HttpResponse
from monitor.models import Load, BW

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
