#!/usr/bin/python
### Usage: python clean-iam-users.py <endpoint-ip>
import sys
import json
from requests import Session

IAM_TOKEN_GENERATION_URL = "{0}/iam/v1/oidc/token"
IAM_USER_ACCESS_KEYS_URL = "{0}/iam/v1/buckets_access_keys"
IAM_USERS_LIST_URL = "{0}/iam/v1/users"

IAM_USER_INFO_URL = IAM_USERS_LIST_URL + '/{1}'
IAM_USER_KEYS_URL = IAM_USER_INFO_URL + '/buckets_access_keys'
IAM_DELETE_KEYS_URL = IAM_USER_KEYS_URL + '/{2}'
IAM_DERIVED_KEY_URL = IAM_USER_ACCESS_KEYS_URL + '/{1}/derived_key'

iam_ip = sys.argv[1]
iam_service = "http://{0}:{1}".format(iam_ip, 5556)

class HTTP(object):

  def __init__(self):
    self._session = Session()

  def _send(self, method, url, **kwargs):
    kwargs['verify'] = kwargs.get('verify', False)
    if 'json' in kwargs:
        kwargs['data'] = json.dumps(kwargs['json'])
        content_dict = {'content-type': 'application/json'}
        kwargs.setdefault('headers', {})
        kwargs['headers'].update(content_dict)
        del kwargs['json']
    func = getattr(self._session, method)

    response = func(url, **kwargs)
    self._session.close()
    return response

_http = HTTP()

def setup_http_auth():
    body = {'grant_type': 'password'}
    header = {"Content-Type": "application/x-www-form-urlencoded"}
    _http._session.headers = None
    _http._session.auth = ('admin', 'Nutanix.123')
    url = IAM_TOKEN_GENERATION_URL.format(iam_service)
    resp = _http._send('post', url, headers=header, data=body, verify=False)
    content = json.loads(resp.content)
    _bearer_token = content['id_token']
    _http._session.auth = None
    common_header = {"Content-Type": "application/json",
                     "Authorization": "Bearer %s" % _bearer_token}
    _http._session.headers = common_header


def list_users():
    url = IAM_USERS_LIST_URL.format(iam_service)
    resp = _http._send('get', url)
    return json.loads(resp.content)


def delete_user(user_id):
    url = IAM_USER_INFO_URL.format(iam_service, user_id)
    resp = _http._send('delete', url)
    print (resp)

def cleanup_users(user_prefix = ''):
    users = list_users()
    for user_info in users['users']:
        user_name = user_info['username']
        print "Found User/UserType : %s"%(user_name)
        if user_info['username'] != 'admin' and user_info['username'].startswith(user_prefix):
            print " - Deleting user %s"%(user_name)
            delete_user(user_info['uuid'])
        else:
            print " - User type is admin, skiping user deletion : %s"%(user_name)

setup_http_auth()
cleanup_users()
