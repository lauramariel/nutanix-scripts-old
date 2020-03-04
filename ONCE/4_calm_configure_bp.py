#!/usr/local/bin/python3

import json
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Script to configure blueprint

# User defined variables
PC_IP =  "34.83.19.200"
AUTH_TYPE = HTTPBasicAuth("admin", '*7YSBFMa34')
PROJECT_NAME = "default"
BP_NAME = "MyApp"
SUBNET_NAME = "default-net"
IMAGE_NAME = "CentOS-7-x86_64-1810.qcow2"
MYSQL_PASSWORD = "nutanix/4u"
LAB_PRIVATE_KEY = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAii7qFDhVadLx5lULAG/ooCUTA/ATSmXbArs+GdHxbUWd/bNG\nZCXnaQ2L1mSVVGDxfTbSaTJ3En3tVlMtD2RjZPdhqWESCaoj2kXLYSiNDS9qz3SK\n6h822je/f9O9CzCTrw2XGhnDVwmNraUvO5wmQObCDthTXc72PcBOd6oa4ENsnuY9\nHtiETg29TZXgCYPFXipLBHSZYkBmGgccAeY9dq5ywiywBJLuoSovXkkRJk3cd7Gy\nhCRIwYzqfdgSmiAMYgJLrz/UuLxatPqXts2D8v1xqR9EPNZNzgd4QHK4of1lqsNR\nuz2SxkwqLcXSw0mGcAL8mIwVpzhPzwmENC5OrwIBJQKCAQB++q2WCkCmbtByyrAp\n6ktiukjTL6MGGGhjX/PgYA5IvINX1SvtU0NZnb7FAntiSz7GFrODQyFPQ0jL3bq0\nMrwzRDA6x+cPzMb/7RvBEIGdadfFjbAVaMqfAsul5SpBokKFLxU6lDb2CMdhS67c\n1K2Hv0qKLpHL0vAdEZQ2nFAMWETvVMzl0o1dQmyGzA0GTY8VYdCRsUbwNgvFMvBj\n8T/svzjpASDifa7IXlGaLrXfCH584zt7y+qjJ05O1G0NFslQ9n2wi7F93N8rHxgl\nJDE4OhfyaDyLL1UdBlBpjYPSUbX7D5NExLggWEVFEwx4JRaK6+aDdFDKbSBIidHf\nh45NAoGBANjANRKLBtcxmW4foK5ILTuFkOaowqj+2AIgT1ezCVpErHDFg0bkuvDk\nQVdsAJRX5//luSO30dI0OWWGjgmIUXD7iej0sjAPJjRAv8ai+MYyaLfkdqv1Oj5c\noDC3KjmSdXTuWSYNvarsW+Uf2v7zlZlWesTnpV6gkZH3tX86iuiZAoGBAKM0mKX0\nEjFkJH65Ym7gIED2CUyuFqq4WsCUD2RakpYZyIBKZGr8MRni3I4z6Hqm+rxVW6Dj\nuFGQe5GhgPvO23UG1Y6nm0VkYgZq81TraZc/oMzignSC95w7OsLaLn6qp32Fje1M\nEz2Yn0T3dDcu1twY8OoDuvWx5LFMJ3NoRJaHAoGBAJ4rZP+xj17DVElxBo0EPK7k\n7TKygDYhwDjnJSRSN0HfFg0agmQqXucjGuzEbyAkeN1Um9vLU+xrTHqEyIN/Jqxk\nhztKxzfTtBhK7M84p7M5iq+0jfMau8ykdOVHZAB/odHeXLrnbrr/gVQsAKw1NdDC\nkPCNXP/c9JrzB+c4juEVAoGBAJGPxmp/vTL4c5OebIxnCAKWP6VBUnyWliFhdYME\nrECvNkjoZ2ZWjKhijVw8Il+OAjlFNgwJXzP9Z0qJIAMuHa2QeUfhmFKlo4ku9LOF\n2rdUbNJpKD5m+IRsLX1az4W6zLwPVRHp56WjzFJEfGiRjzMBfOxkMSBSjbLjDm3Z\niUf7AoGBALjvtjapDwlEa5/CFvzOVGFq4L/OJTBEBGx/SA4HUc3TFTtlY2hvTDPZ\ndQr/JBzLBUjCOBVuUuH3uW7hGhW+DnlzrfbfJATaRR8Ht6VU651T+Gbrr8EqNpCP\ngmznERCNf9Kaxl/hlyV5dZBe/2LIK+/jLGNu9EJLoraaCBFshJKF\n-----END RSA PRIVATE KEY-----"

HEADERS = {'Content-type': 'application/json'}

def get_project_uuid():
	get_project_url = "https://{}:9440/api/nutanix/v3/projects/list".format(PC_IP)
	project_details = requests.post(get_project_url, auth=AUTH_TYPE, headers=HEADERS, data='{"filter":"name=='+ PROJECT_NAME +'"}', verify=False)
	if project_details.ok:
		parsed_project_details = json.loads(project_details.content)
		project_uuid = str(parsed_project_details["entities"][0]["metadata"]["uuid"])
	return project_uuid

def get_blueprint_uuid():
	get_bp_url = "https://{}:9440/api/nutanix/v3/blueprints/list".format(PC_IP)
	bp_details = requests.post(get_bp_url, auth=AUTH_TYPE, headers=HEADERS, data='{"filter":"name=='+ BP_NAME +'"}', verify=False)
	if bp_details.ok:
		parsed_bp_details = json.loads(bp_details.content)
		bp_uuid = str(parsed_bp_details["entities"][0]["metadata"]["uuid"])
	return bp_uuid

def get_subnet_uuid():
	get_subnet_url = "https://{}:9440/api/nutanix/v3/subnets/list".format(PC_IP)
	subnet_details = requests.post(get_subnet_url, auth=AUTH_TYPE, headers=HEADERS, data='{"filter":"name=='+ SUBNET_NAME +'"}', verify=False)
	if subnet_details.ok:
		parsed_subnet_details = json.loads(subnet_details.content)
		subnet_uuid = str(parsed_subnet_details["entities"][0]["metadata"]["uuid"])
	return subnet_uuid

def get_image_uuid():
	get_image_url = "https://{}:9440/api/nutanix/v3/images/list".format(PC_IP)
	image_details = requests.post(get_image_url, auth=AUTH_TYPE, headers=HEADERS, data='{"filter":"name=='+ IMAGE_NAME +'"}', verify=False)
	if image_details.ok:
		parsed_image_details = json.loads(image_details.content)
		image_uuid = str(parsed_image_details["entities"][0]["metadata"]["uuid"])
	return image_uuid

def get_blueprint_details(blueprint_uuid):
	get_bp_url = "https://{}:9440/api/nutanix/v3/blueprints/".format(PC_IP)+str(blueprint_uuid)
	bp_details = requests.get(get_bp_url, auth=AUTH_TYPE, headers=HEADERS, data='{}', verify=False)
	if bp_details.ok:
		parsed_bp_details = json.loads(bp_details.content)
	return parsed_bp_details

# Modify the given blueprint from get_blueprint_details()
def modify_blueprint(blueprint_details, subnet_uuid, image_uuid, assigned_ip):
	new_bp = blueprint_details 
	print("Removing status entity")
	new_bp.pop('status', None)
	print("Updating account_UUID in substrate_definition_list to " + subnet_uuid)
	new_bp['spec']['resources']['substrate_definition_list'][0]['create_spec']['resources']['account_uuid'] = subnet_uuid
	print("Updating image UUID in disk_list to " + image_uuid)
	new_bp['spec']['resources']['substrate_definition_list'][0]['create_spec']['resources']['disk_list'][0]['data_source_reference']['uuid'] = image_uuid
	print("Updating subnet_reference UUID to " + subnet_uuid)
	new_bp['spec']['resources']['substrate_definition_list'][0]['create_spec']['resources']['nic_list'][0]['subnet_reference']['uuid'] = subnet_uuid
	print("Updating ip_endpoint_list to " + assigned_ip)
	new_bp['spec']['resources']['substrate_definition_list'][0]['create_spec']['resources']['nic_list'][0]['ip_endpoint_list'] = [{"ip": assigned_ip, "type":"ASSIGNED"}]
	print("updating mysql_password")
	new_bp['spec']['resources']['app_profile_list'][0]['variable_list'][2]['value'] = MYSQL_PASSWORD # how can we grab it by value and not assume it's the 2nd index?
	print("updating credentials")
	new_bp['spec']['resources']['credential_definition_list'][0]['secret']['attrs']['is_secret_modified'] = "true"
	new_bp['spec']['resources']['credential_definition_list'][0]['secret']['value'] = LAB_PRIVATE_KEY
	return new_bp

	
def update_blueprint(blueprint_uuid, new_bp):
	url = "https://{}:9440/api/nutanix/v3/blueprints/".format(PC_IP)+str(blueprint_uuid)
	configure_resp = requests.put(url, auth=AUTH_TYPE, headers=HEADERS, data=new_bp, verify=False)
	print("{} {}".format(configure_resp, url))
	if configure_resp.ok:
		print("Blueprint configured successfully.")
	else:
		print("An error occurred when configuring the blueprint.")


if __name__=="__main__":
	project_uuid = get_project_uuid()
	blueprint_uuid = get_blueprint_uuid()
	blueprint_details = get_blueprint_details(blueprint_uuid)
	subnet_uuid = get_subnet_uuid()
	image_uuid = get_image_uuid()
	assigned_ip = "172.31.0.203"

	f = open("old_bp.json", "w")
	print(json.dump(blueprint_details, f))

	new_bp = modify_blueprint(blueprint_details, subnet_uuid, image_uuid, assigned_ip)
	
	f = open("new_bp.json", "w")
	print(json.dump(new_bp, f))

	update_blueprint(blueprint_uuid, json.dumps(new_bp))
