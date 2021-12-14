import utils
from google.cloud import firestore
from datetime import datetime, timezone, timedelta
import pytz

DB = firestore.Client(project="nutanix-testdrive-10")

deploy_stage = 'stage'
# show progress of currently provisioning clusters
clusters = utils.search_clusters(deploy_stage, "state", "PROCESSING")
for cluster in clusters: 
	cluster_info = utils.get_cluster(cluster, deploy_stage) 
	progress = cluster_info.get("progress") 
	gcp_id = cluster_info.get("gcp_id")
	local_tz = pytz.timezone('America/Los_Angeles')
	start_time = cluster_info.get("_Cluster__gcp_start").replace(tzinfo=timezone.utc).astimezone(local_tz)
	assigned_to = cluster_info.get('assigned_to')
	aws_region = cluster_info.get('aws_region')
	print(f"{cluster:20} {gcp_id} {progress:5} {start_time} {aws_region} {assigned_to} ") 

# fix all FAILED clusters and ensure htey have a status of failed and assigned_to is cleared
clusters = utils.search_clusters('stage', "state", "FAILED")
for cluster in clusters: 
	cluster_info = utils.get_cluster(cluster, 'stage') 
	state = cluster_info.get("state") 
	status = cluster_info.get("status") 
	print(status) 
	doc = DB.collection('stagecluster').document(cluster)
	ref = doc.get().to_dict()
	ref["status"] = 'failed'
	ref["assigned_to"] = ''
	doc.set(ref, merge=True)

cluster_info = utils.get_cluster('clusters0aa37wv22n', 'stage') 
state = cluster_info.get("state") 
status = cluster_info.get("status") 
print(status) 
doc = DB.collection('stagecluster').document('clusters0aa37wv22n')
ref = doc.get().to_dict()