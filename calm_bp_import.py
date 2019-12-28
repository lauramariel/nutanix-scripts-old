#!/usr/local/bin/python3

# Script to bulk import Calm blueprints in a given directory
# Can also pass a single filename to it with -f
# Note: currently only processes json files in a single directory, does not traverse a directory structure

import argparse
import getpass
import os
import json
import re
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser(description='Script to import Calm blueprints automatically from a directory, or a single file')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-d", help="Directory to read from, required if -f is not present.")
group.add_argument("-f", help="File to import, required if -d is not present. Full file path required.")
parser.add_argument("-j", required=True, help="Project to import to")
parser.add_argument("-p", required=True, help="Prism Central IP")
parser.add_argument("-u", required=True, help="Prism User")

# Process arguments
args = parser.parse_args()

if args.d is not None:
	DIRPATH = args.d
if args.f is not None:
	FILEPATH = args.f

PROJECT_NAME = args.j
PC_IP = args.p
PC_USER = args.u

# Prompt for password
PC_PASS = getpass.getpass()

# Set auth_type
AUTH_TYPE = HTTPBasicAuth(PC_USER, PC_PASS)

# Set headers
HEADERS = {'Content-type': 'application/json'}

def get_project_uuid():
	get_project_url = "https://{}:9440/api/nutanix/v3/projects/list".format(PC_IP)
	project_details = requests.post(get_project_url, auth=AUTH_TYPE, headers=HEADERS, data='{"filter":"name=='+ PROJECT_NAME +'"}', verify=False)
	if project_details.ok:
		parsed_project_details = json.loads(project_details.content)
		project_uuid = str(parsed_project_details["entities"][0]["metadata"]["uuid"])
	return project_uuid


def import_blueprint(bp_name, bp_file, project_uuid):
	import_url = "https://{}:9440/api/nutanix/v3/blueprints/import_file".format(PC_IP)
 
	file_to_upload = {'file': open(bp_file, 'rb')}
	data = {'name': bp_name, 'project_uuid': project_uuid }
	#print("File object to upload: " + format(file_to_upload))
	#print("Data to upload: " + format(data))

	print("Processing file " + bp_file)

	import_resp = requests.post(import_url, auth=AUTH_TYPE, files=file_to_upload, data=data, verify=False)
	if import_resp.ok:
		print("Blueprint " + bp_name + " imported successfully")
	else:
		print("Blueprint " + bp_name + " not imported")
		print(import_resp)

if __name__=="__main__":
	project_uuid = get_project_uuid()
	# read files from given directory

	if 'DIRPATH' in globals():
		files = os.scandir(DIRPATH)
		processed = 0 # number of blueprints processed
		unprocessed = 0
		for f in files:
			# f itself is a DirEntry object
			# we have to extract the name with .name 
			jsonfile = re.search("\.json$", f.name)
			if (jsonfile):
				print("======== Processing " + f.name + " ========")
				bp_name = f.name[:-5] # Extract just the filename (everything before .json)
				print("BP name will be: " + bp_name)
				path_to_file = f.path
				print("Path to file: " + path_to_file)
				import_blueprint(bp_name, path_to_file, project_uuid)
				processed += 1
				print()
			else:
				print("======== Not processing " + f.name + " (Doesn't appear to be a JSON file) ========")
				unprocessed +=1
				print()
		print(format(processed) + " files processed")
		print(format(unprocessed) + " files not processed")

	if 'FILEPATH' in globals():
		print("Only processing one file.")
		print(FILEPATH)
		bp_name = os.path.split(FILEPATH)[1][:-5]
		path_to_file = FILEPATH
		import_blueprint(bp_name, path_to_file, project_uuid)






