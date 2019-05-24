#!/usr/bin/python

import boto3
import glob
import re
import logging
import warnings
from botocore.exceptions import ClientError
from botocore.exceptions import EndpointConnectionError
from botocore.client import Config
warnings.filterwarnings("ignore")

# This script uploads all files in a given directory as objects to the specified bucket

### user defined variables ###
endpoint_ip = "10.42.242.81" #Replace this value
access_key_id = "7OKXhJe-_QXdfe9NegeUEj32c9vUQzyx"
secret_access_key = "CRN4DBysKr_LZk9CaKXsLL449ydC5hE6"
bucket = "archives"
name_of_dir = "sample-files"

# concatenate full endpoint URL
endpoint_url = "https://"+endpoint_ip+":443"

# set connection timeout
config = Config(connect_timeout=5, retries={'max_attempts': 0})

# set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(asctime)s: %(message)s',filename="upload_to_bucket.log")

# set up s3 client
session = boto3.session.Session()
s3client = session.client(service_name="s3", aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key, endpoint_url=endpoint_url, verify=False,config=config)

# return the list of file path names
filepath = glob.glob("%s/*" % name_of_dir)

# go through all the files in the list and upload them
for current in filepath:
    object_data = open(current, 'rb')
    regex_string = re.escape(name_of_dir)+"/(.*)"
    m=re.search(regex_string, current, re.IGNORECASE)
    if m:
      object_name=m.group(1)
    try:
       s3client.put_object(Bucket=bucket, Body=object_data, Key=object_name)
    except ClientError as e:
       logging.error(e)
       exit(1)
    except EndpointConnectionError as e:
       logging.error(e)
       exit(1)
    logging.info("Successfully uploaded %s" % object_name)