#!/bin/bash

new_instance_name=$1

if [ -z $new_instance_name ]; then
  echo "Usage: $0 <instance_name>"
  echo "No instance provided, exiting"
  exit 1
fi

# get external IP

# external_ip=`gcloud compute instances describe $new_instance_name .... tbd
external_ip=`gcloud compute instances describe $new_instance_name --format=json | jq -r .networkInterfaces[].accessConfigs[].natIP`
echo $external_ip
destination_ip="{{destination_ip}}" # where the proxy should forward to
password="{{set_a_root_password}}" # put anything here

# sleep before logging in to make sure it's come up all the way
sleep 10

# this assumes SSH keys are set up for the following user
user="laura"

# check if it's accessible via ssh
status=1
attempts=0
while [ $status != 0 ]; do
  attempts=$((i+1))
  if [ $attempts == 5 ]; then
    echo "Quitting after 5th attempt, configure VM manually."
    exit 1
  fi
  ssh $user@$external_ip 'hostname'
  status=$?
  echo "status = $status"
done

# change root password so the instance can be accessed via serial console after forwarding is enabled
# set iptables nat rules to forward to $destination_ip

ssh $user@$external_ip "printf \"%s\n\" $password $password | sudo passwd ; sudo iptables -t nat -A PREROUTING -j DNAT --to-destination $destination_ip ; sudo iptables -t nat -A POSTROUTING -j MASQUERADE ; sudo sysctl net.ipv4.ip_forward=1"

# sudo iptables -t nat -A PREROUTING -j DNAT --to-destination $destination_ip
# sudo iptables -t nat -A POSTROUTING -j MASQUERADE
# sudo sysctl net.ipv4.ip_forward=1
