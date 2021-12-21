#!/usr/local/bin/python3

import json
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Script to import blueprints to existing project

# User defined variables
PC_IP =  "{{pc_ip}}
AUTH_TYPE = HTTPBasicAuth("admin", '{{password}}')
PROJECT_NAME = "{{project_name}}"
BP_NAME = "{{blueprint_name}}"
PATH_TO_FILE = "{{path_to_blueprint_file}}" # location of blueprint on local machine


def get_project_uuid():
	get_project_url = "https://{}:9440/api/nutanix/v3/projects/list".format(PC_IP)
	headers = {'Content-type': 'application/json'}
	project_details = requests.post(get_project_url, auth=AUTH_TYPE, headers=headers, data='{"filter":"name=='+ PROJECT_NAME +'"}', verify=False)
	if project_details.ok:
		parsed_project_details = json.loads(project_details.content)
		project_uuid = str(parsed_project_details["entities"][0]["metadata"]["uuid"])
	return project_uuid

def import_blueprint(bp_name, bp_file, project_uuid):
	import_url = "https://{}:9440/api/nutanix/v3/blueprints/import_file".format(PC_IP)
	
	file_to_upload = {'file': open(bp_file, 'rb')}
	data = {'name': bp_name, 'project_uuid': project_uuid }
	print(file_to_upload)
	print(data)

	import_resp = requests.post(import_url, auth=AUTH_TYPE, files=file_to_upload, data=data, verify=False)
	if import_resp.ok:
		print("Blueprint " + bp_name + " imported successfully")
	else:
		print("Blueprint " + bp_name + " not imported")

if __name__=="__main__":
  project_uuid = get_project_uuid()
  import_blueprint(BP_NAME, PATH_TO_FILE, project_uuid)

