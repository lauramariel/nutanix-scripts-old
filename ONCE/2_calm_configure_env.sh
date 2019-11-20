#!/bin/bash
#set -x

########################
# User Defined Variables
########################

pcip="35.203.140.64"
password='F5!2GK0NYl'
project_name="default"
network_name="default-net"
image_name="CentOS-7-x86_64-1810.qcow2"

########################
# Set required variables
########################

# Get network_uuid for network_name
url="https://$pcip:9440/api/nutanix/v3/subnets/list"
network_uuid=`curl --silent --insecure -X POST $url -H 'Content-Type: application/json' --user admin:"$password" -d '{"filter": "", "kind": "subnet", "sort_order": "ASCENDING", "offset": 0, "length": 20, "sort_attribute": "string"}' | jq -r ".entities[] | select(.spec.name==\"$network_name\").metadata.uuid"`
echo "Network UUID for $network_name: $network_uuid"

# Get image_uuid for image_name
url="https://$pcip:9440/api/nutanix/v3/images/list"
image_uuid=`curl --silent --insecure -X POST $url -H 'Content-Type: application/json' --user admin:"$password" -d '{"filter": "", "kind": "image", "sort_order": "ASCENDING", "offset": 0, "length": 20, "sort_attribute": "string"}' | jq -r ".entities[] | select(.spec.name==\"$image_name\").metadata.uuid"`
echo "Image UUID for $image_name: $image_uuid"

# Get project_uuid for project_name
url="https://$pcip:9440/api/nutanix/v3/projects/list"
project_uuid=`curl --silent --insecure -X POST  $url -H 'Content-Type: application/json' --user admin:"$password"   -d '{"kind": "project", "length": 20, "offset": 0, "filter": "" }' | jq -r ".entities[] | select(.spec.name==\"$project_name\").metadata.uuid"`
echo "Project UUID for $project_name: $project_uuid"

# Get environment_uuid
# this actually returns nothing if environment isn't configured yet
#url="https://$pcip:9440/api/nutanix/v3/projects_internal/$project_uuid"
#environment_uuid=`curl --silent --insecure -X GET $url -H  'Content-Type: application/json' --user admin:"$password" | jq -r ".status.project_status.resources.environment_reference_list[].uuid"`
#echo "Environment UUID: $environment_uuid"

# Generate timestamp
creation_time=`date +%Y-%m-%dT%H:%M:%SZ`

#################################################################################
# Configure Project
#
# 1. Set Nutanix as Provider <== should already be done by 1_calm_add_provider.sh
# 2. Set environment variables <== this script
#
# Requirements for payload: project_uuid, network_uuid,
#                           network_name, project_name (default),
#                           env_uuid (generated)
#################################################################################

echo "Configuring environment on $project_name $project_uuid"

# Generate a project environment uuid for the provider we added
env_uuid=$(uuidgen | tr -d '\n' | tr '[:upper:]' '[:lower:]')

# POST https://$pcip:9440/api/nutanix/v3/environments
url="https://$pcip:9440/api/nutanix/v3/environments"
curl --silent --insecure -X POST $url -H 'Content-Type: application/json' --user admin:"$password" -d "{
  \"api_version\": \"3.0\",
  \"metadata\": {
    \"kind\": \"environment\",
    \"uuid\": \"$env_uuid\"
  },
  \"spec\": {
    \"name\": \"$(uuidgen | tr -d '\n' | tr '[:upper:]' '[:lower:]')\",
    \"resources\": {
      \"substrate_definition_list\": [
        {
          \"variable_list\": [],
          \"type\": \"AHV_VM\",
          \"os_type\": \"Linux\",
          \"action_list\": [],
          \"create_spec\": {
            \"name\": \"vm-@@{calm_array_index}@@-@@{calm_time}@@\",
            \"resources\": {
              \"disk_list\": [
                {
                  \"data_source_reference\": {
                    \"kind\": \"image\",
                    \"name\": \"$image_name\",
                    \"uuid\": \"$image_uuid\"
                  },
                  \"device_properties\": {
                    \"device_type\": \"DISK\",
                    \"disk_address\": {
                      \"device_index\": 0,
                      \"adapter_type\": \"SCSI\"
                    }
                  }
                }
              ],
              \"nic_list\": [
                {
                  \"subnet_reference\": {
                    \"uuid\": \"$network_uuid\"
                  },
                  \"ip_endpoint_list\": []
                }
              ],
              \"boot_config\": {
                \"boot_device\": {
                  \"disk_address\": {
                    \"device_index\": 0,
                    \"adapter_type\": \"SCSI\"
                  }
                }
              },
              \"num_sockets\": 2,
              \"num_vcpus_per_socket\": 1,
              \"memory_size_mib\": 2048
            },
            \"categories\": {}
          },
          \"name\": \"Untitled\",
          \"readiness_probe\": {
            \"connection_type\": \"SSH\",
            \"connection_port\": 22,
            \"address\": \"@@{platform.status.resources.nic_list[0].ip_endpoint_list[0].ip}@@\"
          },
          \"editables\": {
            \"create_spec\": {
              \"resources\": {
                \"nic_list\": {},
                \"serial_port_list\": {}
              }
            }
          },
          \"uuid\": \"$(uuidgen | tr -d '\n' | tr '[:upper:]' '[:lower:]')\"
        }
      ],
      \"credential_definition_list\": [
        {
          \"name\": \"CENTOS\",
          \"type\": \"KEY\",
          \"username\": \"centos\",
          \"secret\": {
            \"attrs\": {
              \"is_secret_modified\": true
            },
            \"value\": \"-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAii7qFDhVadLx5lULAG/ooCUTA/ATSmXbArs+GdHxbUWd/bNG\nZCXnaQ2L1mSVVGDxfTbSaTJ3En3tVlMtD2RjZPdhqWESCaoj2kXLYSiNDS9qz3SK\n6h822je/f9O9CzCTrw2XGhnDVwmNraUvO5wmQObCDthTXc72PcBOd6oa4ENsnuY9\nHtiETg29TZXgCYPFXipLBHSZYkBmGgccAeY9dq5ywiywBJLuoSovXkkRJk3cd7Gy\nhCRIwYzqfdgSmiAMYgJLrz/UuLxatPqXts2D8v1xqR9EPNZNzgd4QHK4of1lqsNR\nuz2SxkwqLcXSw0mGcAL8mIwVpzhPzwmENC5OrwIBJQKCAQB++q2WCkCmbtByyrAp\n6ktiukjTL6MGGGhjX/PgYA5IvINX1SvtU0NZnb7FAntiSz7GFrODQyFPQ0jL3bq0\nMrwzRDA6x+cPzMb/7RvBEIGdadfFjbAVaMqfAsul5SpBokKFLxU6lDb2CMdhS67c\n1K2Hv0qKLpHL0vAdEZQ2nFAMWETvVMzl0o1dQmyGzA0GTY8VYdCRsUbwNgvFMvBj\n8T/svzjpASDifa7IXlGaLrXfCH584zt7y+qjJ05O1G0NFslQ9n2wi7F93N8rHxgl\nJDE4OhfyaDyLL1UdBlBpjYPSUbX7D5NExLggWEVFEwx4JRaK6+aDdFDKbSBIidHf\nh45NAoGBANjANRKLBtcxmW4foK5ILTuFkOaowqj+2AIgT1ezCVpErHDFg0bkuvDk\nQVdsAJRX5//luSO30dI0OWWGjgmIUXD7iej0sjAPJjRAv8ai+MYyaLfkdqv1Oj5c\noDC3KjmSdXTuWSYNvarsW+Uf2v7zlZlWesTnpV6gkZH3tX86iuiZAoGBAKM0mKX0\nEjFkJH65Ym7gIED2CUyuFqq4WsCUD2RakpYZyIBKZGr8MRni3I4z6Hqm+rxVW6Dj\nuFGQe5GhgPvO23UG1Y6nm0VkYgZq81TraZc/oMzignSC95w7OsLaLn6qp32Fje1M\nEz2Yn0T3dDcu1twY8OoDuvWx5LFMJ3NoRJaHAoGBAJ4rZP+xj17DVElxBo0EPK7k\n7TKygDYhwDjnJSRSN0HfFg0agmQqXucjGuzEbyAkeN1Um9vLU+xrTHqEyIN/Jqxk\nhztKxzfTtBhK7M84p7M5iq+0jfMau8ykdOVHZAB/odHeXLrnbrr/gVQsAKw1NdDC\nkPCNXP/c9JrzB+c4juEVAoGBAJGPxmp/vTL4c5OebIxnCAKWP6VBUnyWliFhdYME\nrECvNkjoZ2ZWjKhijVw8Il+OAjlFNgwJXzP9Z0qJIAMuHa2QeUfhmFKlo4ku9LOF\n2rdUbNJpKD5m+IRsLX1az4W6zLwPVRHp56WjzFJEfGiRjzMBfOxkMSBSjbLjDm3Z\niUf7AoGBALjvtjapDwlEa5/CFvzOVGFq4L/OJTBEBGx/SA4HUc3TFTtlY2hvTDPZ\ndQr/JBzLBUjCOBVuUuH3uW7hGhW+DnlzrfbfJATaRR8Ht6VU651T+Gbrr8EqNpCP\ngmznERCNf9Kaxl/hlyV5dZBe/2LIK+/jLGNu9EJLoraaCBFshJKF\n-----END RSA PRIVATE KEY-----\"
          },
          \"uuid\": \"$(uuidgen | tr -d '\n' | tr '[:upper:]' '[:lower:]')\"
        }
      ]
    }
  }
}"

# PUT https://$pcip:9440/api/nutanix/v3/projects_internal/$project_uuid
url="https://$pcip:9440/api/nutanix/v3/projects_internal/$project_uuid"
curl --silent --insecure -X PUT $url -H 'Content-Type: application/json' --user admin:"$password" -d "{
  \"spec\": {
    \"access_control_policy_list\": [],
    \"project_detail\": {
      \"name\": \"$project_name\",
      \"resources\": {
        \"account_reference_list\": [],
        \"environment_reference_list\": [
          {
            \"kind\": \"environment\",
            \"uuid\": \"$env_uuid\"
          }
        ],
        \"user_reference_list\": [],
        \"external_user_group_reference_list\": [],
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
    \"spec_version\": 1,
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
