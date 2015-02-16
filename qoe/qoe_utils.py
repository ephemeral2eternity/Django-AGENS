## Implement QoE related methods used in qoe.views etc.
# Chen Wang, Feb. 16, 2015
# chenw@cmu.edu
import json
from qoe.models import QoE
from overlay.models import Server

# ================================================================================
# Initialize the QoE vector for all servers on current agent
# ================================================================================
def initializeQoE():
	existingQoE = QoE.objects.all()
	if existingQoE.count() > 0:
		existingQoE.delete()
	srvs = Server.objects.all()
	for s in srvs:
		print("Initialize QoE for server", s.name)
		if s.isLocal:
			q = 5.0
		else:
			q = 4.0
		cur_qoe = QoE(qoe=q, srv=s.name)
		cur_qoe.save()

# ================================================================================
# Return the dict of QoE traces with key defined as server name
# ================================================================================
def getQoEStr():
	qoe_dict = {}
	srvs = Server.objects.all()
	for s in srvs:
		qoe_dict[s.name] = []
		srv_qoes = QoE.objects.filter(srv=s.name)
		for q in srv_qoes:
			ts_str = q.time.strftime('%Y-%m-%d %H:%M:%S')
			qoe_out_str = ts_str + " ------- " + str(q.qoe)
			qoe_dict[s.name].append(qoe_out_str)
	return qoe_dict
