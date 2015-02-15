## Read locally cached videos from folder vidlist
import socket
import os
import ntpath
import urllib2
from overlay.models import Peer
from video.models import Video

def get_local_videos():
	full_path = os.path.realpath(__file__)
	cur_folder, cur_file = ntpath.split(full_path)
	vidlist_folder = cur_folder + '/vidlists/'
	hostname = get_local_name()

	vidlist_file = vidlist_folder + hostname
	f = open(vidlist_file, 'r')

	vidlist = []
	for line in f:
		vid_id = int(line)
		vidlist.append(vid_id)

	# print(vidlist)
	return vidlist

def get_local_name():
	return str(socket.gethostname())

def get_real_local_videos():
	cached_videos = []
	abspath = os.path.expanduser("~/videos/")
	dirs = filter(os.path.isdir, [os.path.join(abspath, f) for f in os.listdir(abspath)]) # ; print flist
	# print "Locally cached videos are: ", dirs
	for video in dirs:
		cached_videos.append(ntpath.basename(video))
	return cached_videos

def periodic_discover():
	caching_list = {}
	cur_host = get_local_name()
	local_videos = Video.objects.all().values_list('id')
	local_video_ids = [int(vid[0]) for vid in local_videos]
	caching_list[cur_host] = local_video_ids
	peers = Peer.objects.all()
	for peer in peers:
		update_videos(peer.ip, caching_list)

def update_videos(peer_ip, caching_list):
	update_url = 'http://%s:8615/video/add/'%peer_ip
	update_data = urllib2.urlencode(caching_list)
	header = {'User-Agent': 'AGENS Cache Agent'}

	req = urllib2.Request(update_url, update_data, header)
	rsp = urllib2.urlopen(req)

#cached_videos = get_real_local_videos()
#print(cached_videos)
