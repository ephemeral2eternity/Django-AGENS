## Read locally cached videos from folder vidlist
import socket
import os
import ntpath
import urllib.request
import urllib.parse
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

# ================================================================================
# Update the list of locally cached videos to peers every hour
# ================================================================================
def periodic_discover():
	caching_list = {}
	cur_host = get_local_name()
	local_videos = Video.objects.all().values_list('id')
	local_video_id_str = ', '.join(str(vid[0]) for vid in local_videos)
	caching_list[cur_host] = local_video_id_str
	peers = Peer.objects.all()
	for peer in peers:
		update_videos(peer.ip, caching_list)

# ================================================================================
# Forward updated video info to other peers
# @input : rcv_host --- the peer that updates come from
#          video_updates --- updates made on local host
# ================================================================================
def forward_updates(rcv_host, video_updates):
	all_peers = Peer.objects.all()
	for peer in all_peers:
		if rcv_host != peer.name:
			update_videos(peer.ip, video_updates)

# ================================================================================
# Update the videos in caching_list to a peer
# ================================================================================
def update_videos(peer_ip, caching_list):
	update_url = 'http://%s:8615/video/add/'%peer_ip
	update_data = urllib.parse.urlencode(caching_list)
	data = data.encode('utf-8')

	req = urllib.request.Request(update_url, update_data)
	rsp = urllib.request.urlopen(req)
	rspData = rsp.read()
	print(rspData)

# ================================================================================
# Change the dictionary of list for video updates to the string version
# @input : update_list --- the dictionary of video updates with keys as servers and
#			values as list of video ids.
# @return: update_str --- the dictionary of video updates in string version. Keys
#			are servers and values are strings of the list of video ids.
# ================================================================================
def update_list2str(update_list):
	update_str = {}
	for srv in update_list.keys():
		vid_list = update_list[srv]
		vid_list_str = ', '.join(str(vid) for vid in vid_list)
		update_str[srv] = vid_list_str
	return update_str

#cached_videos = get_real_local_videos()
#print(cached_videos)
