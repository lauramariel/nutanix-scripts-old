"""
vm_report.py: Script to get CSV report of certain VM-level metrics
from the v1 API
"""
import requests
import json
import datetime
import urllib3
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

content_type = "application/json"
headers = {"Content-type": f"{content_type}"}

current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
filename = f"report-{current_time}.csv"
f = open(filename, "w")
pe_ip = "<PRISM_ELEMENT_IP>"
password = "<PRISM_ELEMENT_PW>"

# Get Cluster Name for this PE
cluster_url = f"https://{pe_ip}:9440/PrismGateway/services/rest/v1/clusters"
resp = requests.get(
    cluster_url, auth=HTTPBasicAuth("admin", password), headers=headers, verify=False
)
# if resp.ok:
results = json.loads(resp.text)

for i in results["entities"]:
    cluster_name = i["name"]

# URL for Stats of All VM Stats
url = f"https://{pe_ip}:9440/PrismGateway/services/rest/v1/vms"

resp = requests.get(
    url, auth=HTTPBasicAuth("admin", password), headers=headers, verify=False
)

# if resp.ok:
results = json.loads(resp.text)

desired_attributes = [
    "vmName",
    "clusterUuid",
    "numVCpus",
    "memoryCapacityInBytes",
    "diskCapacityInBytes",
]
desired_stats = [
    "hypervisor_cpu_usage_ppm",
    "guest.memory_usage_bytes",
    "memory_usage_ppm",
    "controller_user_bytes",
    "hypervisor_num_received_bytes",
    "hypervisor_num_transmitted_bytes",
]

# print heading
for attr in desired_attributes:
    if attr == "clusterUuid":
        f.write("Cluster Name,")
    else:
        f.write(f"{attr},")
for stat in desired_stats:
    f.write(f"{stat} Max,")
    f.write(f"{stat} Avg,")

f.write("\n")

for vm in results["entities"]:
    for attr in desired_attributes:
        if attr == "clusterUuid":
            # use the cluster name instead
            f.write(f"{cluster_name}" + ",")
        elif "Bytes" in attr:
            # 1073741824 bytes = 1 GiB
            if vm[f"{attr}"]:
                value_in_gib = vm[f"{attr}"] / 1073741824
            else:
                value_in_gib = 0
            f.write(f"{value_in_gib} GiB,")
        else:
            f.write(str(vm[f"{attr}"]) + ",")

    for vm_metric in desired_stats:
        # for this we will query the API for the past 30 days for the specific VM and metric, then calculate the max and average
        vm_uuid = vm["uuid"]
        # calculate epoch time in microseconds for the last 30 days
        startTimeInUsecs = int(
            (datetime.datetime.now() - datetime.timedelta(days=30)).timestamp()
            * 1000000
        )
        new_url = f"{url}/{vm_uuid}/stats/?metrics={vm_metric}&startTimeInUsecs={startTimeInUsecs}"
        # f.write(new_url)

        metric_resp = requests.get(
            new_url,
            auth=HTTPBasicAuth("admin", password),
            headers=headers,
            verify=False,
        )
        metric_results = json.loads(metric_resp.text)

        # f.write(metric_results)
        for i in metric_results["statsSpecificResponses"]:
            if len(i["values"]) > 0:
                max_value = max(i["values"])
                average = sum(i["values"]) / len(i["values"])
            else:
                max_value = 0
                average = 0
            f.write(str(max_value) + ",")
            f.write(str(average) + ",")

    f.write("\n")

f.close()

print(f"Report written to {filename}")
