## This agent is used to monitor the load, outbound bw and user demand on current cache agent
# Chen Wang, Feb. 12, 2015
# chenw@cmu.edu
# cache_monitor.py
import json
import string,cgi,time
import sys
import shutil
from monitor.models import Load, BW

# ================================================================================
# Monitor video server load in last 1 minute. 
# User load is monitored by the number of chunk requests in 1 minute
# ================================================================================
def load_monitor():
	load_list = Load.objects.all()
	load_list_len = load_list.count()
	if load_list_len <= 0:
		total_load = get_load()
		first_load = 0
		first_load_obj = Load(load=first_load, total=total_load)
		first_load_obj.save()
	else:
		print("[Django_crontab] Add load monitored!")
		previous_item = Load.objects.all()[load_list_len - 1]
		print("[Django_crontab] Previous Total Load: " + str(previous_item.total))
		cur_total_load = get_load()
		print("[Django_crontab] Current Total Load: " + str(cur_total_load))
		load_per_minute = cur_total_load - previous_item.total
		print("[Django_crontab] Current Load: " + str(load_per_minute))
		cur_load = Load(load=load_per_minute, total=cur_total_load)
		cur_load.save()
		print("[Django_crontab] Finished saving new load item")

# ================================================================================
# Probe outbound traffic every 1 minutes. 
# ================================================================================
def bw_monitor():
	bw_list = BW.objects.all()
	bw_list_len = bw_list.count()
	if bw_list_len <= 0:
		tx_bytes = get_tx_bytes()
		first_bw = 0
		first_bw_obj = BW(bw=first_bw, tx=tx_bytes)
		first_bw_obj.save()
	else:
		print("[Django_crontab] Add bw monitored!")
		previous_obj = BW.objects.all()[bw_list_len - 1]
		cur_tx = get_tx_bytes()
		cur_bw = float(cur_tx - previous_obj.tx) * 8 / (5 * 60 * 1024 * 1024)
		cur_bw_obj = BW(bw=cur_bw, tx=cur_tx)
		cur_bw_obj.save()
	

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

