#!/bin/bash
#set -x

# Script to import blueprints to existing project

########################
# User Defined Variables
########################

pcip="35.203.140.64"
password='xxxxxxxx'
project_name="default" 
path_to_file1="/Users/laura.jordana/Documents/ONCE/MyApp.json" # location of blueprint on local machine
path_to_file2="/Users/laura.jordana/Documents/ONCE/MyCustomApp.json" # location of blueprint on local machine
app_name1="MyApp"
app_name2="MyNewApp"

########################
# Set required variables
########################

# Get project_uuid for project_name
url="https://$pcip:9440/api/nutanix/v3/projects/list"
project_uuid=`curl --silent --insecure -X POST $url -H 'Content-Type: application/json' --user admin:"$password" -d '{"kind": "project", "length": 20, "offset": 0, "filter": "" }' | jq -r ".entities[] | select(.spec.name==\"$project_name\").metadata.uuid"`

###################################################################################
# Import Blueprint
#
# Requirements: blueprint files (.json) on the system where the API call is made,
#               project_uuid
###################################################################################

url="https://$pcip:9440/api/nutanix/v3/blueprints/import_file"
echo "Uploading blueprint 1..."
curl --silent --insecure -X POST $url -F file=@$path_to_file1 -F name=$app_name1 -F project_uuid=$project_uuid --user admin:"$password"
echo "Uploading blueprint 2..."
curl --silent --insecure -X POST $url -F file=@$path_to_file2 -F name=$app_name2 -F project_uuid=$project_uuid --user admin:"$password"
