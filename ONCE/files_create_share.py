#!/usr/local/bin/python3
#
# Script to create a SMB share on an existing file server
# Author: Laura Jordana
# Date: 2/5/2020
# Tested on AOS 5.11

import json
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# User defined variables
PE_IP =  "10.38.9.134"
PC_IP = "10.38.9.137"
PE_AUTH_TYPE = HTTPBasicAuth("admin", 'nx2Tech295!')
PC_AUTH_TYPE = HTTPBasicAuth("admin", 'nx2Tech295!')
SUBNET_NAME = "default-net"
FILES_VERSION = "3.6.1.1"
FILESERVER_NAME = "filesvr1" # File server to create the share on
SHARE_NAME = "MyShare" # Desired name of share
PROTOCOL = "SMB" # SMB or NFS


# Set required variables
HEADERS = {'Content-type': 'application/json'}

def get_fileserver_uuid():
	get_fs_url = "https://{}:9440/PrismGateway/services/rest/v1/vfilers/?searchString={}".format(PE_IP, str(FILESERVER_NAME))
	fs_details = requests.get(get_fs_url, auth=PE_AUTH_TYPE, headers=HEADERS, data='{}', verify=False)
	print('{} {}'.format(fs_details, get_fs_url))
	if fs_details.ok:
		parsed_fs_details = json.loads(fs_details.content)
		fs_uuid = str(parsed_fs_details["entities"][0]["uuid"])
		return fs_uuid
	return 

def create_share(fs_uuid):
	url = "https://{}:9440/PrismGateway/services/rest/v1/vfilers/{}/shares".format(PE_IP, str(fs_uuid))
	payload = {
	    "name": SHARE_NAME,
	    "fileServerUuid": fs_uuid,
	    "enablePreviousVersion": "true",
	    "windowsAdDomainName": "ntnxlab.local",
	    "description": "",
	    "maxSizeGiB": 0,
	    "protocolType": PROTOCOL,
	    "secondaryProtocolType": "NONE",
	    "sharePath": "",
	    "isNestedShare": "false",
	    "enableAccessBasedEnumeration": "true",
	    "enableSmb3Encryption": "false",
	    "shareType": "GENERAL"
	}

	print(json.dumps(payload))
	resp = requests.post(url, auth=PE_AUTH_TYPE, headers=HEADERS, data=json.dumps(payload), verify=False)
	print('{} {}'.format(resp, url))

if __name__ == "__main__":
	fileserver_uuid = get_fileserver_uuid()
	create_share(fileserver_uuid)
