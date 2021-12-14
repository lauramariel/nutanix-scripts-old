#!/bin/bash
set -x

# Script to create GCP instance in the same subnet as a given instance (identified by its external IP)

########################
# user defined variables
########################

# project to use
project="{{gcp_project}}"

# external IP of a given instance
external_ip="{{external_ip}}"

# zone the instance is in
zone="{{zone}}"

# desired instance name prefix
new_instance_prefix="{{prefix}}"

# disk image to use
disk_image="ubuntu-minimal-1604-xenial-v20191217"  # get image list from gcloud compute images list
disk_image_project="ubuntu-os-cloud"

##############
# script start
##############

# set project
gcloud config set project $project

# set zone
gcloud config set compute/zone $zone

# get existing instance info
existing_instance=`gcloud compute instances list | grep $external_ip | awk '{print $1}'`

if [ -z $existing_instance ]; then
  echo "Instance with external_ip $external_ip not found, exiting."
  exit 1
else
  echo "Found instance $existing_instance"
fi

# get existing instance UUID
instance_uuid=`echo $existing_instance | cut -f4 -d-`

# set new instance name based on existing UUID
new_instance_name=$new_instance_prefix-$instance_uuid

# get subnet from existing instance
network=`gcloud compute instances describe $existing_instance --format="json" | jq -r ".networkInterfaces[].network" | cut -f10 -d/`
subnet="$network-subnet"

# create instance within this VPC
gcloud compute instances create $new_instance_name --image $disk_image --image-project $disk_image_project --network $network --subnet $subnet --can-ip-forward

# enable connecting to serial ports
gcloud compute instances add-metadata $new_instance_name --metadata serial-port-enable=true

# update firewall rules
gcloud compute firewall-rules create prismproproxy-$instance_uuid --allow tcp:80,tcp:8080 --network $network

# configure the new host with firewall rules
./gcp_configure_proxy.sh $new_instance_name
