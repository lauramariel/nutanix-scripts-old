#!/usr/local/bin/python3

import uuid
import json
import sys
import requests
import copy
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Script to deploy files
# Requires domain controller to be configured already

# User defined variables
PE_IP =  "10.38.6.70"
PC_IP = "10.38.6.73"
PE_AUTH_TYPE = HTTPBasicAuth("admin", 'nx2Tech265!')
PC_AUTH_TYPE = HTTPBasicAuth("admin", 'nx2Tech265!')
SUBNET_NAME = "default-net"
FILES_VERSION = "3.6.1.1"

# Domain controller info
AUTH_FQDN = "ntnxlab.local"
AUTH_ADMIN_USER = "administrator@ntnxlab.local"
AUTH_ADMIN_PASS = "nutanix/4u"
AUTH_HOST = "10.38.6.101"


# Set required variables
HEADERS = {'Content-type': 'application/json'}

def get_subnet_uuid():
	get_subnet_url = "https://{}:9440/api/nutanix/v3/subnets/list".format(PC_IP)
	subnet_details = requests.post(get_subnet_url, auth=PC_AUTH_TYPE, headers=HEADERS, data='{"filter":"name=='+ SUBNET_NAME +'"}', verify=False)
	print(subnet_details)
	if subnet_details.ok:
		parsed_subnet_details = json.loads(subnet_details.content)
		subnet_uuid = str(parsed_subnet_details["entities"][0]["metadata"]["uuid"])
	return subnet_uuid 

def deploy_files(fileserver_name, subnet_uuid, ntp_server):
	url = "https://{}:9440/PrismGateway/services/rest/v1/vfilers".format(PE_IP)
	payload = {
	   "name": fileserver_name,
	   "numCalculatedNvms":"1",
	   "numVcpus":"4",
	   "memoryGiB":"12",
	   "internalNetwork":{
	      "subnetMask":"",
	      "defaultGateway":"",
	      "uuid": subnet_uuid,
	      "pool":[

	      ]
	   },
	   "externalNetworks":[
	      {
	         "subnetMask":"",
	         "defaultGateway":"",
	         "uuid": subnet_uuid,
	         "pool":[

	         ]
	      }
	   ],
	   "windowsAdDomainName": AUTH_FQDN,
	   "windowsAdUsername": AUTH_ADMIN_USER,
	   "windowsAdPassword": AUTH_ADMIN_PASS,
	   "dnsServerIpAddresses":[
	      AUTH_HOST
	   ],
	   "ntpServers":[
	      ntp_server
	   ],
	   "sizeGib":"1024",
	   "version": FILES_VERSION,
	   "dnsDomainName": AUTH_FQDN,
	   "nameServicesDTO":{
	      "adDetails":{
	         "windowsAdDomainName": AUTH_FQDN,
	         "windowsAdUsername": AUTH_ADMIN_USER,
	         "windowsAdPassword": AUTH_ADMIN_PASS,
	         "addUserAsFsAdmin": "true",
	         "organizationalUnit":"",
	         "preferredDomainController":"",
	         "overwriteUserAccount": "false",
	         "rfc2307Enabled": "false",
	         "useSameCredentialsForDns": "false",
	         "protocolType":"1"
	      }
	   },
	   "addUserAsFsAdmin": "true",
	   "organizationalUnit":"",
	   "preferredDomainController":"",
	   "fsDnsOperationsDTO":{
	      "dnsOpType":"MS_DNS",
	      "dnsServer":"",
	      "dnsUserName": AUTH_ADMIN_USER,
	      "dnsPassword": AUTH_ADMIN_PASS
	   },
	   "pdName": "NTNX-"+ fileserver_name
	}

	print(json.dumps(payload))
	resp = requests.post(url, auth=PE_AUTH_TYPE, headers=HEADERS, data=json.dumps(payload), verify=False)
	print(resp)

if __name__=="__main__":
	fileserver_name = "filesvr1"
	subnet_uuid = get_subnet_uuid()
	ntp_server = "0.pool.ntp.org"
	deploy_files(fileserver_name, subnet_uuid, ntp_server)
