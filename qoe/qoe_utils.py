## Implement QoE related methods used in qoe.views etc.
# Chen Wang, Feb. 16, 2015
# chenw@cmu.edu
import json
import re
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
		s.qoe = q
		s.save()
		# update_overlay_qoe(s.name, q)

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

# ================================================================================
# Update QoE for a server with given new QoE value and an alpha value
# @input : srv ---- the server to update qoe
#	   qoe ---- new qoe value received for the srv
#          alpha ---- the weight to be given to the new QoE value
# ================================================================================
def updateQoE(srv, qoe, alpha):
	last_qoe = QoE.objects.filter(srv=srv).order_by('-time')[0]
	print('Last qoe value for server ', srv, ' is ', last_qoe.qoe)
	previous_qoe = float(last_qoe.qoe)
	new_qoe = (1 - alpha) * previous_qoe + alpha * qoe
	print('New qoe is ', new_qoe)
	new_qoe_obj = QoE(qoe=new_qoe, srv=srv)
	new_qoe_obj.save()
	update_overlay_qoe(srv, new_qoe)

# ================================================================================
# Update QoE value for a server in the overlay table
# @input : srv ---- the server to update qoe
#	   qoe ---- new qoe value to be updated in overlay table
# ================================================================================
def update_overlay_qoe(srv, qoe):
	srv_id = int(re.findall(r'\d+', srv)[0])
	srv_obj = Server.objects.get(pk=srv_id)
	srv_obj.qoe = qoe
	srv_obj.save()
	print('Successfully update qoe for server, ', srv, ' in the overlay table!')
