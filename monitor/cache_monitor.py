## This agent is used to monitor the load, outbound bw and user demand on current cache agent
# Chen Wang, Feb. 12, 2015
# chenw@cmu.edu
# cache_monitor.py
import json
import string,cgi,time
import sys
import shutil
import socket
import urllib.request, urllib.parse
from monitor.models import Load, BW
from overlay.models import Server

# ================================================================================
# Monitor video server load in last 1 minute. 
# User load is monitored by the number of chunk requests in 1 minute
# ================================================================================
def load_monitor():
	load_list = Load.objects.all()
	load_list_len = load_list.count()
	if load_list_len <= 0:
		total_load = get_load()
		load_diff = 0
	else:
		print("[Django_crontab] Add load monitored!")
		previous_item = Load.objects.all()[load_list_len - 1]
		print("[Django_crontab] Previous Total Load: " + str(previous_item.total))
		total_load = get_load()
		print("[Django_crontab] Current Total Load: " + str(total_load))
		load_diff = total_load - previous_item.total
		print("[Django_crontab] Current Load: " + str(load_diff))
	cur_load = Load(load=load_diff, total=total_load)
	cur_load.save()
	update_overlay_load(load_diff)
	print("[Django_crontab] Finished updating new load to all other servers!")

# ================================================================================
# Save the updated load in the overlay table 
# ================================================================================
def update_overlay_load(load):
	cur_srv = get_host_name()
	print("[Django_crontab] It is inside update_overlay_load!")

	## Update load on local server
	cur_srv_obj = Server.objects.filter(isLocal=True)[0]
	cur_srv_obj.load = load
	cur_srv_obj.save()
	print("[Django_crontab] Finished saving new load to local server, ", cur_srv_obj.name)

	## Update other servers about local load
	load_dict = {}
	load_dict['srv'] = cur_srv
	load_dict['load'] = load

	## Send update url to all other servers
	other_srvs = Server.objects.filter(isLocal=False)
	for other_srv in other_srvs:
		other_srv_ip = other_srv.ip
		print('Update monitored load', load_dict, ' to server ', other_srv.name)
		update_overlay_obj(other_srv_ip, load_dict)

# ================================================================================
# Probe outbound traffic every 1 minutes. 
# ================================================================================
def bw_monitor():
	bw_list = BW.objects.all()
	bw_list_len = bw_list.count()
	if bw_list_len <= 0:
		cur_tx = get_tx_bytes()
		cur_bw = 0
	else:
		print("[Django_crontab] Add bw monitored!")
		previous_obj = BW.objects.all()[bw_list_len - 1]
		cur_tx = get_tx_bytes()
		cur_bw = float(cur_tx - previous_obj.tx) * 8 / (5 * 60 * 1024 * 1024)
		print("[Django_crontab] Most Recent BW monitored:", str(cur_bw))
	cur_bw_obj = BW(bw=cur_bw, tx=cur_tx)
	cur_bw_obj.save()
	update_overlay_bw(cur_bw)

# ================================================================================
# Save the updated bw in the overlay table 
# ================================================================================
def update_overlay_bw(bw):
	cur_srv = get_host_name()

	## Update bw on local server
	cur_srv_obj = Server.objects.filter(isLocal=True)[0]
	cur_srv_obj.bw = bw
	cur_srv_obj.save()

	## Update other servers about local load
	bw_dict = {}
	bw_dict['srv'] = cur_srv
	bw_dict['bw'] = bw

	## Send update url to all other servers
	other_srvs = Server.objects.filter(isLocal=False)
	for other_srv in other_srvs:
		other_srv_ip = other_srv.ip
		print('Update monitored bw', bw_dict, ' to server ', other_srv.name)
		update_overlay_obj(other_srv_ip, bw_dict)

# ================================================================================
# Send most recent monitored value obj to remote server by overlay/update url
# @input : srv_ip ---- remote server ip
#	   monitored_dict ---- the dict of monitored value
#			       { 'srv' : cur_host, 'load/bw' : most recent monitored value}
# ================================================================================
def update_overlay_obj(srv_ip, monitored_dict):
	url = 'http://%s:8615/overlay/update?'%srv_ip
	params = urllib.parse.urlencode(monitored_dict)
	url = url + params

	try:
		req = urllib.request.Request(url)
		rsp = urllib.request.urlopen(req)
		rsp_data = rsp.read()
		print(rsp_data)
	except:
		return

# ================================================================================
# Dump the monitored load and bw to google cloud storage gs://agens-data/
# ================================================================================
def dump_monitor():
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
        return ts

# ================================================================================
# Get the number of http chunk requests in every 1 minute
# ================================================================================
def get_load():
	ln_num = -1
	with open('/var/log/apache2/access.log') as f:
		ln_num = len(f.readlines())
	return ln_num


# ================================================================================
# Read outbound bytes every 1 minute. 
# ================================================================================
def get_tx_bytes():
	file_txbytes = open('/sys/class/net/eth0/statistics/tx_bytes')
	lines = file_txbytes.readlines()
	tx_bytes = int(lines[0])
	file_txbytes.close()
	return tx_bytes

# ================================================================================
# Get current host name 
# ================================================================================
def get_host_name():
	return str(socket.gethostname())
