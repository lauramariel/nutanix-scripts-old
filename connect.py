#!/usr/bin/python
### used by cleanup_buckets.py
from botocore.config import Config
import boto3
#boto3.set_stream_logger(name='botocore')

def connect(ip="http://10.42.71.42:7200", aws=False, https=False, **kwargs):
  session = boto3.session.Session()
  config = Config(connect_timeout=120,
                  read_timeout=120,
                  retries={'max_attempts': 0})
  params={}
  params["config"] = config
  params["service_name"] = "s3"
  if aws:
    return session.client(**params)

  params["aws_access_key_id"] = "poseidon_access"
  params["aws_secret_access_key"] = "poseidon_secret"
  params["endpoint_url"] = ip
  params["use_ssl"]=False
  params["verify"]=False
  return session.client(**params)
