#!/usr/bin/env python
# coding: utf-8

import json

from tornado import httpclient

github_api_base = 'https://api.github.com'

def _invoke_api(path, access_token, method='get'):
    global github_api_base
    http_client = httpclient.HTTPClient()
    ret = None
    try:
        resp = http_client.fetch(
                '%s/%s?access_token=%s' % (github_api_base, path, access_token),
                user_agent='tornado http client')
        ret = json.loads(resp.body)
    except httpclient.HTTPError as e:
        print("Error: " + str(e))
    except Exception as e:
        print("Error: " + str(e))
    finally:
        http_client.close()
    return ret


def get_user_info(access_token):
    return _invoke_api('user', access_token)


def get_user_soid(social_user):
    return social_user.get('id', None) if isinstance(social_user, dict) else None


def get_user_soname(social_user):
    return social_user.get('name', None) if isinstance(social_user, dict) else None

