from django_cron import CronJobBase, Schedule
from overlay.ping import *
from overlay.models import Server

class ping_job(CronJobBase):
	"""
	Cron Job that checks the server load and add load info to the db
	"""

	# Run every 1 hour
	run_every = 60
	schedule = Schedule(run_every_mins=run_every)
	code = 'overlay.cron.ping_job'

	# This will be executed every 1 minute
	def do(self):
		srvs = Server.objects.filter(isLocal=False)
		for srv in srvs:
			print("Pinging ", srv.name)
			srv_rtt = getMnRTT(srv.ip, 5)
			srv.rtt = srv_rtt
			print("RTT is:", str(srv_rtt))
			srv.save()
