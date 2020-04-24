#!/usr/local/bin/python3

# before running this script, need to export auth credentials with
# export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"


# Imports the Google Cloud client library
from google.cloud import datastore


# Instantiates a client
client = datastore.Client()

# datastore kind (table)
kind = 'sg-cluster'
query = client.query(kind=kind)
query.add_filter('state', '=', 'FAILED')
query.add_filter('type', '=', 'td2files')
results = list(query.fetch())


# returns one large Entity object

for p in results:
  # returns a dict_items object for each object in Entity object
  items = p.items()
  for key, value in items:
   if key == "gcp_id":
      print(f'{value}')
