#!/usr/local/bin/python3

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth
import json
import sys

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

PC_IP = "35.203.140.64"
AUTHTYPE = HTTPBasicAuth("admin", 'password')
BP_PUBLISH_NAME = "MyApp"

def crudops(url1):
  headers = {'Content-type': 'application/json'}
  r = requests.post(url1, auth=AUTHTYPE, headers=headers, data='{"filter":"name=='+ BP_PUBLISH_NAME +'"}', verify=False)
  if r.ok:
    return json.loads(r.content)
  else:
    sys.exit(r.content)

url1 = "https://{}:9440/api/nutanix/v3/marketplace_items/list".format(PC_IP)
resp1 = crudops(url1)

#get MP UUID
for i in resp1['entities']:
  if i['status']['resources']['app_state'] == 'PENDING' and i['status']['resources']['version'] == '1.0.0':
    mp_uuid = i['metadata']['uuid']


url1="https://{}:9440/api/nutanix/v3/calm_marketplace_items/".format(PC_IP)+str(mp_uuid)
headers = {'Content-type': 'application/json'}
resp = requests.get(url1, auth=AUTHTYPE,headers=headers, verify=False)
payload = json.loads(resp.content)
payload['metadata'].pop('owner_reference', None)
payload.pop('status', None)
payload['metadata'].pop('create_time', None)
payload['spec']['resources']['app_state'] = 'ACCEPTED'
resp = requests.put(url1, auth=AUTHTYPE, headers=headers, data=json.dumps(payload), verify=False)
print(resp.status_code)
if not resp.ok:
  sys.exit(resp.content)
