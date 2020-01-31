#!/usr/local/bin/python3
# Script to enable & deploy Objects on AOS 5.11
# Author: Laura Jordana
# Date: 1/31/2020

import uuid
import json
import sys
import requests
import copy
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Script to deploy Objects on AOS 5.11

# User defined variables
PE_IP =  "10.38.6.70"
PC_IP = "10.38.6.73"
PE_AUTH_TYPE = HTTPBasicAuth("admin", 'nx2Tech265!')
PC_AUTH_TYPE = HTTPBasicAuth("admin", 'nx2Tech265!')
SUBNET_NAME = "default-net"
# Objects specific variables
OBJECTS_DNS_IP = "10.38.6.90" # GCP 172.31.0.3
OBJECTS_VIP = "10.38.6.91" # GCP 172.31.0.4
OBJECTS_CLIENT_IP_START = "10.38.6.92" # GCP 172.31.0.5
OBJECTS_CLIENT_IP_END = "10.38.6.96" # GCP 172.31.0.8


# Set required variables
HEADERS = {'Content-type': 'application/json'}

def get_uuids():
	get_subnet_url = "https://{}:9440/api/nutanix/v3/subnets/list".format(PC_IP)
	subnet_details = requests.post(get_subnet_url, auth=PC_AUTH_TYPE, headers=HEADERS, data='{"filter":"name=='+ SUBNET_NAME +'"}', verify=False)
	if subnet_details.ok:
		parsed_subnet_details = json.loads(subnet_details.content)
		cluster_uuid = str(parsed_subnet_details["entities"][0]["status"]["cluster_reference"]["uuid"])
		subnet_uuid = str(parsed_subnet_details["entities"][0]["metadata"]["uuid"])
	return subnet_uuid, cluster_uuid

def enable_objects():
	print("Checking to see if Objects is already enabled")
	# check to see if objects is already enabled, and if it is, skip this
	urlcheck = "https://{}:9440/oss/api/nutanix/v3/groups".format(PC_IP)
	payloadcheck = {
		"entity_type": "objectstore"
	}
	resp = requests.post(urlcheck, auth=PC_AUTH_TYPE, headers=HEADERS, data=json.dumps(payloadcheck), verify=False)
	#print(resp)
	if resp.ok:
		parsed_resp = json.loads(resp.content)
		if(len(parsed_resp) > 0):
			print("Object store is already enabled")
			return

	print("Enabling Objects")
	url = "https://{}:9440/api/nutanix/v3/services/oss".format(PC_IP)
	payload = {
		"state": "ENABLE"
	}

	print(json.dumps(payload))
	resp = requests.post(url, auth=PC_AUTH_TYPE, headers=HEADERS, data=json.dumps(payload), verify=False)
	print(resp)
        
def deploy_objects(cluster_uuid, subnet_uuid):
	# Need to update to use dark site procedure which is way faster
	print("Deploying Objects")
	url = "https://{}:9440/oss/api/nutanix/v3/objectstores".format(PC_IP)
	payload = {
	  "api_version": "3.0",
	  "metadata": {
	    "kind": "objectstore"
	  },
	  "spec": {
	    "name": "ntnxobjects",
	    "description": "NTNXLAB",
	    "resources": {
	      "domain": "ntnxlab.local",
	      "cluster_reference": {
	        "kind": "cluster",
	        "uuid": cluster_uuid
	      },
	      "buckets_infra_network_dns": OBJECTS_DNS_IP,
	      "buckets_infra_network_vip": OBJECTS_VIP,
	      "buckets_infra_network_reference": {
	        "kind": "subnet",
	        "uuid": subnet_uuid
	      },
	      "client_access_network_reference": {
	        "kind": "subnet",
	        "uuid": subnet_uuid
	      },
	      "aggregate_resources": {
	        "total_vcpu_count": 10,
	        "total_memory_size_mib": 32768,
	        "total_capacity_gib": 51200
	      },
	      "client_access_network_ipv4_range": {
	        "ipv4_start": OBJECTS_CLIENT_IP_START,
	        "ipv4_end": OBJECTS_CLIENT_IP_END
	      }
	    }
	  }
	}

	print(json.dumps(payload))
	resp = requests.post(url, auth=PC_AUTH_TYPE, headers=HEADERS, data=json.dumps(payload), verify=False)
	print(resp)

if __name__=="__main__":
	subnet_uuid, cluster_uuid = get_uuids()
	enable_objects()
	deploy_objects(cluster_uuid, subnet_uuid)