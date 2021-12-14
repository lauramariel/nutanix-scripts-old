#!/usr/local/bin/python3

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth
import json
import sys

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

PC_IP="35.203.140.64"
BP_PUBLISH_NAME = "MyApp"
AUTH_TYPE = HTTPBasicAuth("admin", 'password')
BP_PUBLISH_VERSION = "1.0.0"
PROJECT_NAME = "default"
PROJECT_UUID = "3adb9300-baca-4127-beba-337bc1d91a18" # hardcoded for this sample

def crudops(url1):
  headers = {'Content-type': 'application/json'}
  r = requests.post(url1, auth=AUTH_TYPE, headers=headers, data='{"filter":"name=='+ BP_PUBLISH_NAME +'"}', verify=False)
  print(r.status_code)
  if r.ok:
    return json.loads(r.content)
  else:
    sys.exit(r.content)

url1 = "https://{}:9440/api/nutanix/v3/marketplace_items/list".format(PC_IP)
resp1 = crudops(url1)

print(json.dumps(resp1))
#get MP UUID
for i in resp1['entities']:
  if i['status']['resources']['app_state'] == 'ACCEPTED' and i['status']['resources']['version'] == BP_PUBLISH_VERSION:
    mp_uuid = i['metadata']['uuid']


url1="https://{}:9440/api/nutanix/v3/calm_marketplace_items/".format(PC_IP)+str(mp_uuid)
headers = {'Content-type': 'application/json'}
resp = requests.get(url1, auth=AUTH_TYPE, headers=headers, verify=False)
print(resp.status_code)
payload = json.loads(resp.content)
payload['metadata'].pop('owner_reference', None)
payload.pop('status', None)
payload['metadata'].pop('create_time', None)
#payload['metadata']['categories']['AppFamily'] = ''
payload['spec']['resources']['app_state'] = 'PUBLISHED'
payload['spec']['resources']['project_reference_list'] =[{}]
payload['spec']['resources']['project_reference_list'][0]['kind'] = 'project'
payload['spec']['resources']['project_reference_list'][0]['name'] = PROJECT_NAME
payload['spec']['resources']['project_reference_list'][0]['uuid'] = PROJECT_UUID


resp = requests.put(url1, auth=AUTH_TYPE, headers=headers, data=json.dumps(payload), verify=False)
print(resp.status_code)
if not resp.ok:
  sys.exit(resp.content)

