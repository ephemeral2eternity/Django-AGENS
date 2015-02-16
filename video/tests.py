from django.test import TestCase
import urllib.parse, urllib.request

# Create your tests here.
def update_videos(peer_ip, caching_list):
        url = 'http://%s:8615/video/add/'%peer_ip
        update_data = urllib.parse.urlencode(caching_list)
        data = update_data.encode('utf-8')

        req = urllib.request.Request(url, data)
	req.add_header('REMOTE_HOST', 'cache-07')
        rsp = urllib.request.urlopen(req)
        rspData = rsp.read()
        print(rspData)

peer_ip = '130.211.63.102'
caching_list = {}
local_host = 'cache-07'
local_vid_ids = [1, 2, 3, 4, 5, 6, 8, 9, 11]
local_vid_ids_str = ', '.join(str(item) for item in local_vid_ids)
caching_list[local_host] = local_vid_ids_str

update_videos(peer_ip, caching_list)
