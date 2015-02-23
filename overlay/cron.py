import json
from django_cron import CronJobBase, Schedule
from overlay.ping import *
from overlay.models import Server
from monitor.models import RTTS

class ping_job(CronJobBase):
	"""
	Cron Job that checks the server load and add load info to the db
	"""

	# Run every 1 hour
	run_every = 5
	schedule = Schedule(run_every_mins=run_every)
	code = 'overlay.cron.ping_job'

	# This will be executed every 1 minute
	def do(self):
		rtts = {}
		srvs = Server.objects.filter(isLocal=False)
		for srv in srvs:
			print("Pinging ", srv.name)
			srv_rtt = getMnRTT(srv.ip, 5)
			srv.rtt = srv_rtt
			print("RTT is:", str(srv_rtt))
			srv.save()
			rtts[srv.name] = srv_rtt
		local_srv = Server.objects.filter(isLocal=True)[0]
		rtts[local_srv.name] = 0.0
		rtts_str = json.dumps(rtts)
		rtts_obj = RTTS(rtts=rtts_str)
		rtts_obj.save()
