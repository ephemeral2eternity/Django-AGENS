import random
from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template import RequestContext, loader
from django.http import HttpResponse
from video.models import Video
from video.video_utils import *

# Create your views here.

# The page returned for the request: http://cache_agent_ip:port/videos/
def index(request):
	return query(request)

@csrf_exempt
def initVideo(request):
	# Delete all objects in the table first
	existing_videos = Video.objects.all()
	if existing_videos.count() > 0:
		existing_videos.delete()
	cached_videos = get_local_videos()
	real_cached_videos = get_real_local_videos()
	hostname = get_local_name()
	for vid in cached_videos:
		vid_id = vid
		vid_name = random.choice(real_cached_videos)
		vid_srvs = hostname + ','
		# print("Is ", srv, " the localhost? ", isLocal)
		cur_vid = Video(id=vid_id, name=vid_name, srvs=vid_srvs)
		cur_vid.save()
	return query(request)

@csrf_exempt
def query(request):
	# Return the initialized servers
	vid_list = Video.objects.all()
	cur_host = get_local_name()
	templates = loader.get_template('video/videos.html')
	context = RequestContext(request, {
					'videos' : vid_list,
					'host' : cur_host,
	})
	return HttpResponse(templates.render(context))

@csrf_exempt
def add(request):
	cur_host = get_local_name()
	if request.method == "POST":
		print(request.POST)
		srvs = request.POST.keys()
		for srv in srvs:
			vidlist = request.POST.get(srv, "")
			print(vidlist)
			# for vid in vidlist:
	elif request.method == "GET":
		return HttpResponse("You should use POST method when calling http://cache_agent:port/video/add/ to add video lists!")
				
