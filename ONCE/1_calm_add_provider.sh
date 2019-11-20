#!/bin/bash
#set -x

# Script to add provider to an existing Calm project

########################
# User Defined Variables
########################

pcip="35.203.140.64"
password='F5!2GK0NYl'
project_name="default"
network_name="default-net" 

########################
# Set required variables
########################

# Get network_uuid for network_name
url="https://$pcip:9440/api/nutanix/v3/subnets/list"
network_uuid=`curl --silent --insecure -X POST $url -H 'Content-Type: application/json' --user admin:"$password" -d '{"filter": "", "kind": "subnet", "sort_order": "ASCENDING", "offset": 0, "length": 20, "sort_attribute": "string"}' | jq -r ".entities[] | select(.spec.name==\"$network_name\").metadata.uuid"`
echo "Network UUID for $network_name: $network_uuid"

# Get project_uuid for project_name
url="https://$pcip:9440/api/nutanix/v3/projects/list"
project_uuid=`curl --silent --insecure -X POST $url -H 'Content-Type: application/json' --user admin:"$password" -d '{"kind": "project", "length": 20, "offset": 0, "filter": "" }' | jq -r ".entities[] | select(.spec.name==\"$project_name\").metadata.uuid"`

# Generate timestamp
creation_time=`date +%Y-%m-%dT%H:%M:%SZ`

##################################################################
# Configure Project
#
# 1. Set Nutanix as Provider <== this script
# 2. Set environment variables <== 2_calm_configure_env.sh
#
# Requirements for payload: project_uuid, network_uuid, 
#                           network_name, project_name (default)
##################################################################

echo "Configuring provider on $project_name $project_uuid"

# POST api/nutanix/v3/projects_internal
url="https://$pcip:9440/api/nutanix/v3/projects_internal"
curl --silent --insecure -X POST $url -H 'Content-Type: application/json' --user admin:"$password" -d "{
  \"api_version\": \"3.0\",
  \"metadata\": {
    \"kind\": \"project\",
    \"uuid\": \"$project_uuid\"
  },
  \"spec\": {
    \"project_detail\": {
      \"name\": \"$project_name\",
      \"resources\": {
        \"subnet_reference_list\": [
          {
            \"kind\": \"subnet\",
            \"name\": \"default\",
            \"uuid\": \"$network_uuid\"
          }
        ]
      }
    },
    \"user_list\": [],
    \"user_group_list\": [],
    \"access_control_policy_list\": []
  }
}"

# PUT api/nutanix/v3/projects_internal/$project_uuid
url="https://$pcip:9440/api/nutanix/v3/projects_internal/$project_uuid"
curl --silent --insecure -X PUT $url -H 'Content-Type: application/json' --user admin:"$password" -d "{
  \"spec\": {
    \"access_control_policy_list\": [],
    \"project_detail\": {
      \"name\": \"$project_name\",
      \"resources\": {
        \"account_reference_list\": [],
        \"environment_reference_list\": [],
        \"user_reference_list\": [],
        \"external_user_group_reference_list\": [],
        \"subnet_reference_list\": [
          {
            \"kind\": \"subnet\",
            \"name\": \"$network_name\",
            \"uuid\": \"$network_uuid\"
          }
        ]
      }
    },
    \"user_list\": [],
    \"user_group_list\": []
  },
  \"api_version\": \"3.1\",
  \"metadata\": {
    \"project_reference\": {
      \"kind\": \"project\",
      \"name\": \"$project_name\",
      \"uuid\": \"$project_uuid\"
    },
    \"categories_mapping\": {},
    \"creation_time\": \"$creation_time\",
    \"spec_version\": 0,
    \"kind\": \"project\",
    \"last_update_time\": \"$creation_time\",
    \"uuid\": \"$project_uuid\",
    \"categories\": {},
    \"owner_reference\": {
      \"kind\": \"user\",
      \"name\": \"admin\",
      \"uuid\": \"00000000-0000-0000-0000-000000000000\"
    }
  }
}"
