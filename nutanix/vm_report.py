"""
vm_report.py: Script to get CSV report of certain VM-level metrics
from the v1 API
"""
import requests
import json
import datetime
import urllib3
import sys
import logging
import argparse
import getpass
from base64 import b64encode
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

class RequestParameters:
    """
    Class to hold the parameters of our Request
    """

    def __init__(self, uri, username, password):
        self.uri = uri
        self.username = username
        self.password = password

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"uri={self.uri},"
            f"username={self.username},"
            f"password={self.password},"
        )
class RequestResponse:
    """
    Class to hold the response from our Request
    """

    def __init__(self):
        self.code = 0
        self.message = ""
        self.json = ""
        self.details = ""

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"code={self.code},"
            f"message={self.message},"
            f"json={self.json},"
            f"details={self.details})"
        )


class RESTClient:
    """
    the RESTClient class carries out the actual API request
    by 'packaging' these functions into a dedicated class
    """

    def __init__(self, parameters: RequestParameters):
        self.params = parameters

    def request(self):
        """
        this is the main method that carries out the request
        basic exception handling is managed here, as well as
        returning the response (success or fail), as an instance
        of our RequestResponse
        """
        response = RequestResponse()
        """
        setup the HTTP Basic Authorization header based on the
        supplied username and password
        """
        username = self.params.username
        password = self.params.password
        encoded_credentials = b64encode(
            bytes(f"{username}:{password}", encoding="ascii")
        ).decode("ascii")
        auth_header = f"Basic {encoded_credentials}"

        # Create the headers with the previous creds
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"{auth_header}",
            "cache-control": "no-cache",
        }
        try:
            api_request = requests.get(
                    self.params.uri, headers=headers, timeout=30, verify=False
                )
            # if no exceptions occur here, we can process the response
            response.code = api_request.status_code
            response.message = "Request submitted successfully."
            response.json = api_request.json()
            response.details = "N/A"
        except ValueError:
            # handle when our APIs do not return a JSON body
            response.code = api_request.status_code
            response.message = f"ValueError was caught."
            response.details = "N/A"
        except requests.exceptions.ConnectTimeout:
            # timeout while connecting to the specified IP address or FQDN
            response.code = -95
            response.message = f"Connection has timed out. {username} " + f"{password}"
            response.details = "Exception: requests.exceptions.ConnectTimeout"
        except urllib3.exceptions.ConnectTimeoutError:
            # timeout while connecting to the specified IP address or FQDN
            response.code = -96
            response.message = f"Connection has timed out."
            response.details = "urllib3.exceptions.ConnectTimeoutError"
        except requests.exceptions.MissingSchema:
            # potentially bad URL
            response.code = -97
            response.message = "Missing URL schema/bad URL."
            response.details = "N/A"
        except Exception as _e:
            # unhandled exceptions
            response.code = -99
            response.message = "An unhandled exception has occurred."
            response.details = _e

        return response
class NameFilter(logging.Filter):
    """
    Class to contextually change the log based on the VM being processed
    """
    def __init__(self, vm_name):
        self.vm_name = vm_name

    def filter(self, record):
        record.vm_name = self.vm_name
        return True

def api_request(url, pe_ip, pe_user, pe_password):
    """Create a new entity via a v3 post call, return the response"""

    # Make the API call
    parameters = RequestParameters(
        uri=url,
        username=pe_user,
        password=pe_password
    )
    rest_client = RESTClient(parameters)
    resp = rest_client.request()

    return resp

def custom_log(vm_name):
    """
    Custom log to include current VM name being processed
    """
    logger = logging.getLogger(__name__)
    logger.addFilter(NameFilter(vm_name))
    filelog = logging.FileHandler(filename=f"vm_report-log-{current_time}.log")
    formatter = logging.Formatter("%(levelname).1s %(asctime)s [%(vm_name)s] %(message)s")
    filelog.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    if not logger.hasHandlers():
        logger.addHandler(filelog)
    return logger

def get_cluster_name(pe_ip, pe_user, pe_password):
    """
    Given a Prism Element IP, return the name of the cluster 
    """
    cluster_url = f"https://{pe_ip}:9440/PrismGateway/services/rest/v1/clusters"
    resp = api_request(cluster_url, pe_ip, pe_user, pe_password)

    cluster_info = resp.json

    for i in cluster_info["entities"]:
        cluster_name = i["name"]

    return cluster_name

def main(pe_ip, pe_user, pe_password, report_name, duration):
    content_type = "application/json"
    headers = {"Content-type": f"{content_type}"}
    if not report_name:
        filename = f"vm_report-{current_time}.csv"
    else:
        filename = report_name
    f = open(filename, "w")

    # URL for Stats of All VM Stats
    url = f"https://{pe_ip}:9440/PrismGateway/services/rest/v1/vms"
    logger = custom_log("")
    logger.info(f"{url}")
    logger.info("===========================================")

    resp = api_request(url, pe_ip, pe_user, pe_password)
    results = resp.json

    # this dict maps the desired attribute as obtained from the API
    # with the display name that will be used in the report
    # clusterUuid is coming from a different call but want to be
    # in the second column, so including it here as we'll loop
    # through this later when writing to file
    attributes = {
        "vmName": "Name",
        "clusterUuid": "Parent Cluster",
        "numVCpus": "Provisioned vCPUs",
        "memoryCapacityInBytes": "Memory Capacity",
        "diskCapacityInBytes": "Disk Capacity",
    }

    # this dict maps the desired metric as obtained from the API
    # with the display name that will be used in the report
    metrics = {
        "hypervisor_cpu_usage_ppm": "CPU Usage (%)",
        "guest.memory_usage_bytes": "Memory Consumed (GiB)",
        "memory_usage_ppm": "Memory Usage (%)",
        "controller_user_bytes": "Guest File System Utilization (%)",
        "hypervisor_num_received_bytes": "Network - Data Receive Rate (KBps)",
        "hypervisor_num_transmitted_bytes": "Network - Data Transmit Rate (KBps)",
    }

    # Headings
    for attr in attributes.values():
        f.write(f"{attr},")
    for metric in metrics.values():
        f.write(f"{metric} (Max),")
        f.write(f"{metric} (Average),")

    f.write("\n")

    # Content
    for vm in results["entities"]:
        logger = custom_log(vm["vmName"])
        vm_uuid = vm["uuid"]
 
        for attr in attributes:
            if attr == "clusterUuid":
                # get the Cluster Name
                cluster_name = get_cluster_name(pe_ip, pe_user, pe_password)
                f.write(f"{cluster_name}" + ",")
            elif "Bytes" in attr:
                # 1073741824 bytes = 1 GiB
                if vm[f"{attr}"]:
                    value_in_gib = int(vm[f"{attr}"] / 1073741824)
                else:
                    value_in_gib = 0
                f.write(f"{value_in_gib} GiB,")
            else:
                attribute_value = vm[f"{attr}"]
                f.write(str(attribute_value) + ",")

        for vm_metric, display_name in metrics.items():
            # query the API for the specified duration for the specific VM and metric, then calculate the max and average

            if duration:
                logger.info(f"Getting metrics for last {duration} days")
                startTimeInUsecs = int(
                    (datetime.datetime.now() - datetime.timedelta(days=duration)).timestamp()
                    * 1000000
                )
                metric_url = f"{url}/{vm_uuid}/stats/?metrics={vm_metric}&startTimeInUsecs={startTimeInUsecs}"
            else:
                logger.warning("No duration specified, getting metrics for current point in time")
                metric_url = f"{url}/{vm_uuid}/stats/?metrics={vm_metric}"

            metric_resp = api_request(metric_url, pe_ip, pe_user, pe_password)
            metric_results = metric_resp.json
            logger.info(f"{display_name}: {metric_url}")
            logger.info("===========================================")

            for i in metric_results["statsSpecificResponses"]:
                num_of_values = len(i["values"])
                if num_of_values > 0:
                    max_value = int(max(i["values"]))
                    average = int(float(sum(i["values"]) / num_of_values))

                    logger.info(f"Length of value list: {num_of_values}")
                    logger.info(f"Max Value in value list: {max_value}")
                    logger.info(f"Average Value in value list: {average}")

                    if "controller_user_bytes" in vm_metric:
                        # For Disk Usage report as a %, so need to divide
                        # by total capacity
                        total_disk_cap = vm.get("diskCapacityInBytes")
                        if total_disk_cap:
                            # print("total_disk_cap: " + str(total_disk_cap))
                            max_value = float(
                                "{:.2f}".format((max_value / total_disk_cap) * 100)
                            )
                            average = float(
                                "{:.2f}".format((average / total_disk_cap) * 100)
                            )
                        else:
                            max_value = 0
                            average = 0
                    elif "ppm" in vm_metric:
                        # reported in parts per million, divide by 1e6 and multiply by 100 to get %
                        max_value = float("{:.2f}".format((max_value / 1000000) * 100))
                        average = float("{:.2f}".format((average / 1000000) * 100))
                    elif "memory_usage_bytes" in vm_metric:
                        # convert bytes to GiB - divide by 1073741824
                        max_value = float("{:.2f}".format(max_value / 1073741824))
                        average = float("{:.2f}".format(average / 1073741824))
                    elif "hypervisor_num" in vm_metric:
                        # convert bytes to kilobits - divide by 125
                        max_value = float("{:.2f}".format(max_value / 125))
                        average = float("{:.2f}".format(average / 125))
                    logger.info(f"Max Value after conversion: {max_value}")
                    logger.info(f"Average Value after conversion: {average}")
                    logger.info("===========================================")
                    f.write(f"{max_value},")
                    f.write(f"{average},")
                else:
                    max_value = 0
                    average = 0
                    f.write("0,0,")

        f.write("\n")

    f.close()

    print(f"Report written to {filename}")
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pe_ip", help="Prism Element IP address")
    parser.add_argument("-u", "--username", help="Prism Element username")
    parser.add_argument("-p", "--password", help="Prism Element password")
    parser.add_argument("-d", "--duration", help="Number of days to report on")
    parser.add_argument("-f", "--filename", help="Desired report filename")
    # parser.add_argument("-d", "--debug", help="Enable/disable debug mode")

    args = parser.parse_args()

    pe_user = (
        args.username
        if args.username
        else input("Please enter your Prism Element username: ")
    )
    pe_password = args.password if args.password else getpass.getpass()

    pe_ip = args.pe_ip

    # optional arguments
    report_name = args.filename
    duration = args.duration

    # self.debug = True if args.debug == "enable" else False
    main(pe_ip, pe_user, pe_password, report_name, duration)
