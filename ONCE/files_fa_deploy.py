#!/usr/local/bin/python3
#
# Script to create a SMB share on an existing file server
# This script assumes the container name for the fileserver is Nutanix_<fileservername>_ctr and that the AutoDC2 VM only has one NIC
# And there's no error handling
# Author: Laura Jordana
# Date: 2/5/2020
# Tested on AOS 5.11

import json
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# User defined variables
PE_IP = "10.38.6.70"
PC_IP = "10.38.6.73"
PE_AUTH_TYPE = HTTPBasicAuth("admin", 'nx2Tech265!')
PC_AUTH_TYPE = HTTPBasicAuth("admin", 'nx2Tech265!')
SUBNET_NAME = "default-net"
FA_VERSION = "2.0.1"
FA_VM_NAME = "FA"
FILESERVER_NAME = "filesvr1" # based on what was set in files_deploy.py 
AUTODC_NAME = "AutoDC2"
NTP_SERVERS = "0.pool.ntp.org"

# Set required variables
CTR_NAME = "Nutanix_" + FILESERVER_NAME + "_ctr"
HEADERS = {'Content-type': 'application/json'}

def get_container_uuid():
  get_ctr_url = "https://{}:9440/PrismGateway/services/rest/v2.0/storage_containers".format(PE_IP)
  ctr_details = requests.get(get_ctr_url, auth=PE_AUTH_TYPE, headers=HEADERS, data='{}', verify=False)
  print("{} {}".format(ctr_details, get_ctr_url))
  if ctr_details.ok:
    parsed_ctr_details = json.loads(ctr_details.content)
    for ctr in parsed_ctr_details["entities"]:
      if CTR_NAME in ctr["name"]:
        return(ctr["storage_container_uuid"])


def get_subnet_uuid():
  get_subnet_url = "https://{}:9440/api/nutanix/v3/subnets/list".format(PC_IP)
  subnet_details = requests.post(get_subnet_url, auth=PC_AUTH_TYPE, headers=HEADERS, data='{"filter":"name=='+ SUBNET_NAME +'"}', verify=False)
  print("{} {}".format(subnet_details, get_subnet_url))
  if subnet_details.ok:
    parsed_subnet_details = json.loads(subnet_details.content)
    subnet_uuid = str(parsed_subnet_details["entities"][0]["metadata"]["uuid"])
    return subnet_uuid 

def get_autodc_ip():
  # first a call to get the VM UUID
  get_vm_url = "https://{}:9440/PrismGateway/services/rest/v2.0/vms".format(PE_IP)
  vm_details = requests.get(get_vm_url, auth=PE_AUTH_TYPE, headers=HEADERS, data='{}', verify=False)
  print("{} {}".format(vm_details, get_vm_url))
  if vm_details.ok:
    parsed_vm_details = json.loads(vm_details.content)
    for vm in parsed_vm_details["entities"]:
      if AUTODC_NAME in vm["name"]:
        vm_uuid = vm["uuid"]

  # now a call to look up the IP address of the VM
  get_vm_nic_url = "https://{}:9440/PrismGateway/services/rest/v2.0/vms/{}?include_vm_nic_config=true".format(PE_IP, str(vm_uuid))
  vm_nic_details = requests.get(get_vm_nic_url, auth=PE_AUTH_TYPE, headers=HEADERS, data='{}', verify=False)
  print("{} {}".format(vm_nic_details, get_vm_nic_url))
  if vm_nic_details.ok:
    parsed_details = json.loads(vm_nic_details.content)
    for nic in parsed_details["vm_nics"]:
      return(nic["ip_address"])


def deploy_fa(ctr_uuid, subnet_uuid, auto_dc_ip):
  url = "https://{}:9440/PrismGateway/services/rest/v2.0/analyticsplatform".format(PE_IP)
  #print(url)
  payload = {
    "image_version": FA_VERSION,
    "vm_name": FA_VM_NAME,
    "container_uuid": ctr_uuid,
    "container_name": CTR_NAME,
    "network": {
      "uuid": subnet_uuid,
      "ip": "",
      "netmask": "",
      "gateway": ""
    },
    "resource": {
      "memory": "24",
      "cores": "2",
      "vcpu": "4"
    },
    "dns_servers": [
      auto_dc_ip
    ],
    "ntp_servers": [
      NTP_SERVERS
    ],
    "disk_size": "3"
    }

  print(json.dumps(payload))
  resp = requests.post(url, auth=PE_AUTH_TYPE, headers=HEADERS, data=json.dumps(payload), verify=False)
  print("{} {}".format(resp, url))

if __name__ == "__main__":
  ctr_uuid = get_container_uuid()
  subnet_uuid = get_subnet_uuid()
  auto_dc_ip = get_autodc_ip()
  deploy_fa(ctr_uuid, subnet_uuid, auto_dc_ip)

