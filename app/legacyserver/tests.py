#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'



import urllib
import urllib2
import base64
import unittest
import json





def post_request(params, url, client_id, client_secret):

    s = "{}:{}".format(client_id, client_secret)
    b64 = base64.b64encode(s)
    authorization = 'Basic {}'.format(b64)

    data = urllib.urlencode(params)
    request = urllib2.Request(url, data)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    request.add_header('Authorization', authorization)
    response = urllib2.urlopen(request)
    if response.code == 200:
        tokeninfo = response.read()
        return tokeninfo

def get_request(url, access_token):
    b64 = base64.b64encode(access_token)
    authorization = 'Bearer {}'.format(b64)

    request = urllib2.Request(url)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    request.add_header('Authorization', authorization)
    response = urllib2.urlopen(request)
    if response.code == 200:
        tokeninfo = response.read()
        return tokeninfo


class TestLegacyAuthorize(unittest.TestCase):

    def setUp(self):
        self.url = 'http://127.0.0.1:8000/legacy/authorize'
        self.client_id = "bb0e26df-7da4-4142-9935-7d9086a089bd"
        self.client_secret = "9892d9ab-da50-44e9-91c7-15615a7fc60a"
        self.params = {
            'grant_type': 'password',
            'username': 'admin',
            'password': '123'
        }

    def test_unvalid_client(self):
        error_msg = {'error': 'invalid_client'}
        self.client_id = 'client_id'
        result = json.loads(post_request(self.params, self.url, self.client_id, self.client_secret))
        self.assertDictEqual(error_msg, result)


    def test_unvalid_username_and_password(self):
        error_msg = {'error_description': 'Invalid credentials given.', 'error': 'invalid_grant'}
        # 错误的用户名和密码
        self.params.update(username='username')
        self.params.update(password='password')

        result = json.loads(post_request(self.params, self.url, self.client_id, self.client_secret))
        self.assertDictEqual(error_msg, result)


    def test_unvalid_grant_type(self):
        error_msg = {'error': 'unsupported_grant_type'}
        # 错误的 grant_type
        self.params.update(grant_type='wrong grant_type')
        result = json.loads(post_request(self.params, self.url, self.client_id, self.client_secret))
        self.assertDictEqual(error_msg, result)

    def test_unvalid_scopes(self):
        error_msg = {'error': 'invalid_scope'}
        self.params.update(scope='commons')
        result = json.loads(post_request(self.params, self.url, self.client_id, self.client_secret))
        self.assertDictEqual(error_msg, result)

    def test_default_scopes(self):

        self.params.update(scope='common')
        result = json.loads(post_request(self.params, self.url, self.client_id, self.client_secret))
        self.assertTrue('common', result.get('scopes'))

    def test_access_token(self):
        result = json.loads(post_request(self.params, self.url, self.client_id, self.client_secret))
        self.assertTrue('access_token' in result.keys())
