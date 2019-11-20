#!/bin/bash
set -x

########################
# User Defined Variables
########################

pcip="35.203.140.64"
password='xxxxxxxx'
project_name="default"
network_name="default-net"
image_name="CentOS-7-x86_64-1810.qcow2"
blueprint_name="MyApp"

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

# Get blueprint_uuid for blueprint_name
url="https://$pcip:9440/api/nutanix/v3/blueprints/list"
blueprint_uuid=`curl --silent --insecure -X POST $url -H 'Content-Type: application/json' --user admin:"$password" -d '{"length":20,"offset":0,"filter":"state!=DELETED"}' | jq -r ".entities[] | select(.status.name==\"$blueprint_name\").status.uuid"`
echo "Blueprint UUID for $blueprint_name: $blueprint_uuid"

##################################################################################
# Configure Blueprint
#
# 1. Retrieve existing blueprint that was previously imported (GET)
# 2. Modify returned object
# 3. Upload modified blueprint (PUT)
##################################################################################

# Retrieve existing blueprint
echo "Retrieving blueprint"
url="https://$pcip:9440/api/nutanix/v3/blueprints/$blueprint_uuid"
blueprint=`curl --silent --insecure -X GET $url -H 'Content-Type: application/json' --user admin:"$password"`
#curl --silent --insecure -X GET https://$pcip:9440/api/nutanix/v3/blueprints/$blueprint_uuid -H 'Content-Type: application/json' --user admin:"$password" | jq -r '.spec.resources.substrate_definition_list[].create_spec.resources.guest_customization.cloud_init'

# Set up files to read and write to
jsonfile="$blueprint_name-$blueprint_uuid.json"
tmpjson="$blueprint_name-$blueprint_uuid-tmp.json"
echo $blueprint > $jsonfile

# Modify returned object for the PUT request to configure the blueprint:
# 1. remove status key from returned object
# 2. add account_uuid (same as network_uuid)
# 3. add Mysql_password nutanix/4u 
# 4. Select disk image 
# 5. Select valid NIC
# 6. Add private key for CENTOS cred
# 7. Fix cloud_init formatting if required (yaml spacing disappeared when imported with curl -F)

echo "Modifying blueprint - writing to temp file"

cat $jsonfile \
| jq -c 'del(.status)' \
| jq -c -r "(.spec.resources.substrate_definition_list[].create_spec.resources.account_uuid=\"$network_uuid\")" \
| jq -c -r '(.spec.resources.app_profile_list[].variable_list[] | select(.name == "Mysql_password") | .value) |= "nutanix/4u"' \
| jq -c -r "(.spec.resources.substrate_definition_list[].create_spec.resources.disk_list[].data_source_reference.uuid = \"$image_uuid\")" \
| jq -c -r "(.spec.resources.substrate_definition_list[].create_spec.resources.nic_list[].subnet_reference.uuid =  \"$network_uuid\")" \
| jq -c -r '(.spec.resources.credential_definition_list[].secret.attrs.is_secret_modified = "true")' \
| jq -c -r "(.spec.resources.credential_definition_list[].secret.value=\"-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAii7qFDhVadLx5lULAG/ooCUTA/ATSmXbArs+GdHxbUWd/bNG\nZCXnaQ2L1mSVVGDxfTbSaTJ3En3tVlMtD2RjZPdhqWESCaoj2kXLYSiNDS9qz3SK\n6h822je/f9O9CzCTrw2XGhnDVwmNraUvO5wmQObCDthTXc72PcBOd6oa4ENsnuY9\nHtiETg29TZXgCYPFXipLBHSZYkBmGgccAeY9dq5ywiywBJLuoSovXkkRJk3cd7Gy\nhCRIwYzqfdgSmiAMYgJLrz/UuLxatPqXts2D8v1xqR9EPNZNzgd4QHK4of1lqsNR\nuz2SxkwqLcXSw0mGcAL8mIwVpzhPzwmENC5OrwIBJQKCAQB++q2WCkCmbtByyrAp\n6ktiukjTL6MGGGhjX/PgYA5IvINX1SvtU0NZnb7FAntiSz7GFrODQyFPQ0jL3bq0\nMrwzRDA6x+cPzMb/7RvBEIGdadfFjbAVaMqfAsul5SpBokKFLxU6lDb2CMdhS67c\n1K2Hv0qKLpHL0vAdEZQ2nFAMWETvVMzl0o1dQmyGzA0GTY8VYdCRsUbwNgvFMvBj\n8T/svzjpASDifa7IXlGaLrXfCH584zt7y+qjJ05O1G0NFslQ9n2wi7F93N8rHxgl\nJDE4OhfyaDyLL1UdBlBpjYPSUbX7D5NExLggWEVFEwx4JRaK6+aDdFDKbSBIidHf\nh45NAoGBANjANRKLBtcxmW4foK5ILTuFkOaowqj+2AIgT1ezCVpErHDFg0bkuvDk\nQVdsAJRX5//luSO30dI0OWWGjgmIUXD7iej0sjAPJjRAv8ai+MYyaLfkdqv1Oj5c\noDC3KjmSdXTuWSYNvarsW+Uf2v7zlZlWesTnpV6gkZH3tX86iuiZAoGBAKM0mKX0\nEjFkJH65Ym7gIED2CUyuFqq4WsCUD2RakpYZyIBKZGr8MRni3I4z6Hqm+rxVW6Dj\nuFGQe5GhgPvO23UG1Y6nm0VkYgZq81TraZc/oMzignSC95w7OsLaLn6qp32Fje1M\nEz2Yn0T3dDcu1twY8OoDuvWx5LFMJ3NoRJaHAoGBAJ4rZP+xj17DVElxBo0EPK7k\n7TKygDYhwDjnJSRSN0HfFg0agmQqXucjGuzEbyAkeN1Um9vLU+xrTHqEyIN/Jqxk\nhztKxzfTtBhK7M84p7M5iq+0jfMau8ykdOVHZAB/odHeXLrnbrr/gVQsAKw1NdDC\nkPCNXP/c9JrzB+c4juEVAoGBAJGPxmp/vTL4c5OebIxnCAKWP6VBUnyWliFhdYME\nrECvNkjoZ2ZWjKhijVw8Il+OAjlFNgwJXzP9Z0qJIAMuHa2QeUfhmFKlo4ku9LOF\n2rdUbNJpKD5m+IRsLX1az4W6zLwPVRHp56WjzFJEfGiRjzMBfOxkMSBSjbLjDm3Z\niUf7AoGBALjvtjapDwlEa5/CFvzOVGFq4L/OJTBEBGx/SA4HUc3TFTtlY2hvTDPZ\ndQr/JBzLBUjCOBVuUuH3uW7hGhW+DnlzrfbfJATaRR8Ht6VU651T+Gbrr8EqNpCP\ngmznERCNf9Kaxl/hlyV5dZBe/2LIK+/jLGNu9EJLoraaCBFshJKF\n-----END RSA PRIVATE KEY-----\n\")" \
| jq -r "(.spec.resources.substrate_definition_list[].create_spec.resources.guest_customization.cloud_init.user_data = \"#cloud-config\nusers:\n  - name: centos\n    ssh-authorized-keys:\n      - @@{CENTOS.public_key}@@\n    sudo: ['ALL=(ALL) NOPASSWD:ALL']\")" \
> $tmpjson

# Upload modified blueprint 

url="https://$pcip:9440/api/nutanix/v3/blueprints/$blueprint_uuid"
echo "Uploading modified blueprint for $blueprint_name"

curl --silent --insecure -X PUT $url -H 'Content-Type: application/json' --user admin:"$password" -d @$tmpjson
