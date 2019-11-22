#!/usr/local/bin/python3

import uuid
import json
import sys
import requests
import copy
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Script to add Nutanix provider to an existing Calm project using a specified subnet

# User defined variables
PC_IP =  "35.203.140.64"
AUTH_TYPE = HTTPBasicAuth("admin", 'password')
PROJECT_NAME = "test3"
SUBNET_NAME = "default-net"

# Set required variables
HEADERS = {'Content-type': 'application/json'}

def get_subnet_uuid():
	get_subnet_url = "https://{}:9440/api/nutanix/v3/subnets/list".format(PC_IP)
	subnet_details = requests.post(get_subnet_url, auth=AUTH_TYPE, headers=HEADERS, data='{"filter":"name=='+ SUBNET_NAME +'"}', verify=False)
	if subnet_details.ok:
		parsed_subnet_details = json.loads(subnet_details.content)
		subnet_uuid = str(parsed_subnet_details["entities"][0]["metadata"]["uuid"])
	return subnet_uuid 

def get_project_uuid():
	get_project_url = "https://{}:9440/api/nutanix/v3/projects/list".format(PC_IP)
	project_details = requests.post(get_project_url, auth=AUTH_TYPE, headers=HEADERS, data='{"filter":"name=='+ PROJECT_NAME +'"}', verify=False)
	if project_details.ok:
		parsed_project_details = json.loads(project_details.content)
		project_uuid = str(parsed_project_details["entities"][0]["metadata"]["uuid"])
	return project_uuid

def configure_provider_post(project_uuid, subnet_uuid):
	url1 = "https://{}:9440/api/nutanix/v3/projects_internal".format(PC_IP)
	payload1 = {
		  "api_version": "3.0",
		  "metadata": {
		    "kind": "project",
		    "uuid": project_uuid
		  },
		  "spec": {
		    "project_detail": {
		      "name": PROJECT_NAME,
		      "resources": {
		        "subnet_reference_list": [
		          {
		            "kind": "subnet",
		            "name": "default",
		            "uuid": subnet_uuid
		          }
		        ]
		      }
		    },
		    "user_list": [],
		    "user_group_list": [],
		    "access_control_policy_list": []
		  }
		}

	resp1 = requests.post(url1, auth=AUTH_TYPE, headers=HEADERS, data=json.dumps(payload1), verify=False)
	print(resp1)

def configure_provider_put(project_uuid, subnet_uuid): 
	url2 = "https://{}:9440/api/nutanix/v3/projects_internal/{}".format(PC_IP, str(project_uuid))
	payload2 = { 
  		"spec": {
		    "access_control_policy_list": [],
		    "project_detail": {
		      "name": PROJECT_NAME,
		      "resources": {
		        "account_reference_list": [],
		        "environment_reference_list": [],
		        "user_reference_list": [],
		        "external_user_group_reference_list": [],
		        "subnet_reference_list": [
		          {
		            "kind": "subnet",
		            "name": SUBNET_NAME,
		            "uuid": subnet_uuid
		          }
		        ]
		      }
		    },
		    "user_list": [],
		    "user_group_list": []
		  },
		  "api_version": "3.1",
		  "metadata": {
		    "project_reference": {
		      "kind": "project",
		      "name": PROJECT_NAME,
		      "uuid": project_uuid
		    },
		    "categories_mapping": {},
		    "creation_time": "",
		    "spec_version": 0,
		    "kind": "project",
		    "last_update_time": "",
		    "uuid": project_uuid,
		    "categories": {},
		    "owner_reference": {
		      "kind": "user",
		      "name": "admin",
		      "uuid": "00000000-0000-0000-0000-000000000000"
		    }
		  }
		}

	resp2 = requests.put(url2, auth=AUTH_TYPE, headers=HEADERS, data=json.dumps(payload2), verify=False)
	print(resp2)

if __name__=="__main__":
	subnet_uuid = get_subnet_uuid()
	project_uuid = get_project_uuid()
#	configure_provider_post(project_uuid, subnet_uuid) # need to further test if this is required or not 
	configure_provider_put(project_uuid, subnet_uuid)
