#!/bin/bash
#
# This script compares the external IP address assigned to the GKE nodes (gcloud compute instances describe) 
# with the IPs in the external IP list (gcloud compute addresses list)
# to see if it lost its IP or not
#
# Author: laura@nutanix.com
# Date: 09-22-2020

prefix="gke-testdrive"
project="nutanix-expo"
dir="/tmp"

gcloud compute instances list | grep $prefix > /tmp/compute_instances.txt
gcloud compute addresses list --project $project > /tmp/static_ips.txt

IFS=$'\n' read -r -d '' -a nodes < <( cat $dir/compute_instances.txt | awk '{print $1}' && printf '\0' ) 
IFS=$'\n' read -r -d '' -a zones < <( cat $dir/compute_instances.txt | awk '{print $2}' && printf '\0' ) 

count=0
for i in ${nodes[@]}; do
  ext_ip=`gcloud compute instances describe ${i} --zone ${zones[$count]} | grep natIP | awk '{print $2}'`
  # check if external IP is in the static list
  match=`cat $dir/static_ips.txt | grep $ext_ip`
  if [ -z "$match" ]
  then
    printf "%-50s\t\t%s\t\t%s\n" "$i" "$ext_ip" "ephemeral"
  else
    printf "%-50s\t\t%s\t\t%s\n" "$i" "$ext_ip" "static"
  fi
  count=$((count+1))
done