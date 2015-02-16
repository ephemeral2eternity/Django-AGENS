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
	qoe_dict = getQoEDict()
	print(qoe_dict)
	templates = loader.get_template('qoe/qoes.html')
	context = RequestContext(request, {
					'qoes' : qoe_dict,
	})
	return HttpResponse(templates.render(context))
