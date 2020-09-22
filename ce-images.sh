#!/bin/bash
# Script to see what images are running on the relay and pods for Cloud Engine
# Author: laura@nutanix.com
# Date: 09-03-2020

echo "Relay Image In Use"
echo "=================="
echo "[prod]"
gcloud compute instances describe relay-nutanixtestdrive-com-1-production --zone us-west1-c | grep -i image
gcloud compute instances describe relay-nutanixtestdrive-com-2-production --zone us-west1-b | grep -i image
gcloud compute instances describe relay-nutanixtestdrive-com-3-production --zone us-west1-a | grep -i image
echo 
echo "[stage]"
gcloud compute instances describe relay-staging-nutanixtestdrive-com-1-stage --zone us-west1-c | grep -i image
gcloud compute instances describe relay-staging-nutanixtestdrive-com-2-stage --zone us-west1-b | grep -i image

echo 
echo "Cloud Engine Image In Use"
echo "========================="
echo "[prod]"
kubectl get deploy prod-engine -o yaml --cluster gke_nutanix-expo_us-west1_testdrive-prod  | grep -i "image:"
echo
echo "[stage]"
kubectl get deploy tdc-engine -o yaml --cluster gke_nutanix-expo_us-west1_testdrive-staging | grep -i "image:"
