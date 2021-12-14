
"""
vm_stats.py: Sample script to get all stats from a particular VM, using v1 APIs.
Prints out each key value pair returned.
For the "stats" key (which is a dict), it will indent and print out
the individual key/value pairs within that key. These are all the 
point-in-time stats.
"""

import requests
import json
import urllib3
from requests.auth import HTTPBasicAuth
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# User defined vars
pe_ip="<PRISM ELEMENT IP>"
password="<PRISM ELEMENT PASSWORD>"
vm_uuid="<VM_UUID>"

# System vars
endpoint="/PrismGateway/services/rest/v1/vms"
content_type="application/json"
headers={ "Content-type": f"{content_type}" }

# All VMs
url_all=f"https://{pe_ip}:9440/{endpoint}"

# Specific VM
url_vm=f"https://{pe_ip}:9440/{endpoint}/{vm_uuid}"

resp = requests.get(url_vm, auth=HTTPBasicAuth("admin", password), headers=headers, verify=False)
#print(resp)

results = json.loads(resp.text)

#print(results)
for k,v in results.items():
    if k == "stats":
        print(f"{k}:")
        for k2, v2 in results["stats"].items():
            print(f"      {k2}: {v2}")
    else:
        print(f"{k}: {v}")


