#!/usr/local/bin/python3
#
# Script to deploy files on AOS 5.11
# Requires domain controller (AutoDC2) to be configured already
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

# User defined variables
PE_IP =  "{{pe_ip}}"
PC_IP = "{{pc_ip}}"
PE_AUTH_TYPE = HTTPBasicAuth("admin", '{{pe_password}}')
PC_AUTH_TYPE = HTTPBasicAuth("admin", '{{pc_password}}')
SUBNET_NAME = "default-net"
FILES_VERSION = "3.6.1.1"
FILESERVER_NAME = "filesvr1"
NTP_SERVERS = "{{{ntp_server}}"
# Domain controller info
AUTH_FQDN = "{{domain}}"
AUTH_ADMIN_USER = "{{ad_user}}"
AUTH_ADMIN_PASS = "{{ad_password}}"
AUTH_HOST = "{{ad_ip}}"

# Set required variables
HEADERS = {'Content-type': 'application/json'}

def get_subnet_uuid():
	get_subnet_url = "https://{}:9440/api/nutanix/v3/subnets/list".format(PC_IP)
	subnet_details = requests.post(get_subnet_url, auth=PC_AUTH_TYPE, headers=HEADERS, data='{"filter":"name=='+ SUBNET_NAME +'"}', verify=False)
	print("{} {}".format(subnet_details, get_subnet_url))
	if subnet_details.ok:
		parsed_subnet_details = json.loads(subnet_details.content)
		subnet_uuid = str(parsed_subnet_details["entities"][0]["metadata"]["uuid"])
	return subnet_uuid 

def deploy_files(subnet_uuid):
	url = "https://{}:9440/PrismGateway/services/rest/v1/vfilers".format(PE_IP)
	payload = {
	   "name": FILESERVER_NAME,
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
	      NTP_SERVERS
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
	   "pdName": "NTNX-"+ FILESERVER_NAME
	}

	print(json.dumps(payload))
	resp = requests.post(url, auth=PE_AUTH_TYPE, headers=HEADERS, data=json.dumps(payload), verify=False)
	print("{} {}".format(resp, url))

if __name__=="__main__":
	subnet_uuid = get_subnet_uuid()
	deploy_files(subnet_uuid)
