from django_cron import CronJobBase, Schedule
from monitor.cache_monitor import *

class load_job(CronJobBase):
	"""
	Cron Job that checks the server load and add load info to the db
	"""

	# Run every 1 minute
	run_every = 5
	schedule = Schedule(run_every_mins=run_every)
	code = 'monitor.cron.load_job'

	# This will be executed every 1 minute
	def do(self):
		load_monitor()
		bw_monitor()
