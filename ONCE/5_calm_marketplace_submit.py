#!/usr/local/bin/python3

import uuid
import json
import sys
import requests
import copy
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BP_NAME = "MyApp"
BP_PUBLISH_NAME = "MyApp"
PC_IP = "35.203.140.64"
AUTH_TYPE = HTTPBasicAuth("admin", 'password')
BP_PUBLISH_VERSION = "1.0.0"

APP_GROUP_UUID = uuid.uuid4()
HEADERS = {'Content-type': 'application/json'}

bp_list_url = "https://{}:9440/api/nutanix/v3/blueprints/list".format(PC_IP)
get_user_url = "https://{}:9440/api/nutanix/v3/users/me".format(PC_IP)
publish_mpi_url = "https://{}:9440/api/nutanix/v3/calm_marketplace_items".format(PC_IP)

def get_bp_spec():
	bp_details = requests.post(bp_list_url, auth=AUTH_TYPE, headers=HEADERS, data='{"filter":"name=='+ BP_NAME +'"}', verify=False)
	if bp_details.ok:
		parsed_bp_details = json.loads(bp_details.content)
		bp_uuid = str(parsed_bp_details["entities"][0]["metadata"]["uuid"])
		bp_url = "https://{}:9440/api/nutanix/v3/blueprints/{}/export_json".format(PC_IP, str(bp_uuid))
		bp_export = requests.get(bp_url, auth=AUTH_TYPE, headers=HEADERS, data='{}', verify=False)
	if bp_export.ok:
		return json.loads(bp_export.content)

def get_user_spec():
	user_details = requests.get(get_user_url, auth=AUTH_TYPE, headers=HEADERS, data='{}', verify=False)
	if user_details.ok:
		parsed_user_details = json.loads(user_details.content)
	return parsed_user_details

def generate_and_publish_mpi(blueprint, user_details):
	current_user = user_details["status"]["name"]
	blueprint["spec"]["name"] = BP_PUBLISH_NAME
	blueprint["status"]["name"] = BP_PUBLISH_NAME
	bp_spec = copy.deepcopy(blueprint["spec"])
	bp_status = copy.deepcopy(blueprint["status"])
	del blueprint["spec"]["resources"]
	del blueprint["status"]
	blueprint["metadata"]["kind"] = "marketplace_item"
	blueprint["spec"]["resources"] = {"app_attribute_list": ["FEATURED"]}
	blueprint["spec"]["resources"]["app_group_uuid"] = str(APP_GROUP_UUID)
	blueprint["spec"]["resources"]["author"] = current_user
	blueprint["spec"]["resources"]["icon_reference_list"] = []
	blueprint["spec"]["resources"]["version"] = BP_PUBLISH_VERSION
	blueprint["spec"]["resources"]["app_blueprint_template"] = {"spec": bp_spec}
	blueprint["spec"]["resources"]["app_blueprint_template"]["status"] = bp_status

	publish_mpi_out = requests.post(publish_mpi_url, auth=AUTH_TYPE, headers=HEADERS, data=json.dumps(blueprint), verify=False)
	if publish_mpi_out.ok:
		print("Triggered publish")
	else:
		sys.exit(publish_mpi_out.content)

if __name__=="__main__":
	blueprint = get_bp_spec()
	user_details = get_user_spec()
	generate_and_publish_mpi(blueprint, user_details)
