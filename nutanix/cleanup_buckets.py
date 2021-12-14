#!/usr/bin/python
### Usage to delete all buckets: python cleanup_buckets.py ""
import sys
import math
import time
import datetime
import threading
import connect
import warnings
warnings.filterwarnings("ignore")
ovmip=sys.argv[1].strip()
ip="https://"+ovmip+":7200"
ovm = connect.connect(ip)

def INFO(msg):
  print datetime.datetime.today().strftime('%Y-%m-%d.%H.%M.%S'), msg

if "aws" in ovmip:
  INFO("RUNNING clean up on aws")
  ovm = session.client(service_name=service_name)

bucketprefix=""
try:
  bucketprefix=sys.argv[2].strip()
except:
  bucketprefix=""


def convert_size(size_bytes):
  if size_bytes == 0:
    return "0B"
  size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
  i = int(math.floor(math.log(size_bytes, 1024)))
  p = math.pow(1024, i)
  s = round(size_bytes / p, 2)
  return "%s %s" % (s, size_name[i])

def abort(bu):
  up =  ovm.list_multipart_uploads(Bucket=bu["Name"])
  if up.get("Uploads"):
    for upload in up.get("Uploads"):
      INFO(upload.get("UploadId"))
      try:
        ovm.abort_multipart_upload(Bucket=bu["Name"], UploadId=upload.get("UploadId"), Key=upload.get("Key"))
      except:
        INFO("Failed to abort %s on %s" %(upload.get("UploadId"), upload.get("Key")))

total_objs=0
total_bucs=0
INFO("Initiating List")
bss = ovm.list_buckets()["Buckets"]
INFO("Total buckets found : "+str(len(bss)))
#INFO(ovm.list_buckets()
total_size = 0
start_time=time.time()
for bu in bss:
  if bucketprefix  not in bu["Name"]:
    continue
  threads=[]
  #abort(bu)
  bucket=bu["Name"]
  INFO("BUCKET "+bucket)
  try:
    INFO(" - Listing : "+bucket)
    #objects = ovm.list_objects(Bucket=bucket)
  except Exception as err:
    INFO("  - ERROR : Skipping %s , Error : %s"%(bucket, err))
    continue
  keynum=0
  Objects=[]
  paginator = ovm.get_paginator("list_objects")
  iterator = paginator.paginate(Bucket=bucket)
  INFO("  - Deleting objects using pagination")
  try:
    for item in iterator:
      for obj in item.get("Contents", []):
        lstime=time.time()
        Objects.append({"Key" :obj["Key"]})
        res= ovm.head_object(Bucket=bucket,Key=obj["Key"])
        total_size = total_size + res["ContentLength"]
        if len(Objects) == 1000:
          stime=time.time()
          ovm.delete_objects(Bucket=bucket,Delete={"Objects":Objects})
          INFO(" Deleted 1k objects from : "+str(bucket)+", time taken : "\
            ""+str(time.time() - stime)+", List took : "+str(stime-lstime)+""\
            ""+", Freed up size : "+str(convert_size(total_size)))
          total_objs = total_objs + 1000
          Objects=[]
  except Exception as err:
    INFO("  - ERROR : deleting objects from %s, ERROR : %s"%(bucket, err))
    continue
  if Objects:
    stime=time.time()
    ovm.delete_objects(Bucket=bucket,Delete={"Objects":Objects})
    INFO(" Deleted "+str(len(Objects))+" objects from : "+str(bucket)+", time "\
    "taken : "+str(time.time() - stime))
    total_objs = total_objs + len(Objects)
    Objects=[]
  #INFO(objects.keys()
  #INFO(dir(ovm)
  version =  ovm.list_object_versions(Bucket=bucket)

  if version and version.get("DeleteMarkers"):
    for i in version.get("DeleteMarkers"):
      vid = i.get("VersionId")
      INFO(" Deleting key : "+i.get("Key")+" version : "+vid)
      Objects.append({"Key" :i.get("Key"), "VersionId":vid})
      if len(Objects) == 1000:
        ovm.delete_objects(Bucket=bucket,Delete={"Objects":Objects})
        total_objs = total_objs + len(Objects)
        Objects=[]
    if Objects:
      ovm.delete_objects(Bucket=bucket,Delete={"Objects":Objects})
      total_objs = total_objs + len(Objects)
      Objects=[]
  if version and version.get("Versions"):
    for i in version.get("Versions"):
      vid = i.get("VersionId")
      ovm.delete_object(Bucket=bucket, Key=i.get("Key"), VersionId=vid)
      total_objs = total_objs + 1
  INFO(" Deleting Bucket : "+bucket)
  targs={"Bucket":bucket}
  ovm.delete_bucket(**targs)
  total_bucs += 1
  INFO(" Buckets/Object Deleted : "+str(total_bucs)+"/"+str(total_objs)+""\
        ", Total Freed Space : "+str(convert_size(total_size))+", Total time "\
        "taken : "+str(time.time()-start_time))
  #INFO("Deleting bucket : ", bucket
  #ovm.delete_bucket(Bucket=bucket)
  INFO("*"*10)
