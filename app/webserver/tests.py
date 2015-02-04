#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'


import unittest
import urllib2
import urllib

{
    "scopes": "",
    "grant_type": "authorization_code",
}


url = 'http://127.0.0.1:8000/web/authorize?client_id=b3d127c7-a021-4cb9-aa48-8c77bb06952d','(invalid_request) Missing response_type parameter.'


url = 'http://127.0.0.1:8000/web/authorize?client_id=b3d127c7-a021-4cb9-aa48-8c77bb06952d&response_type=code',\
      '(invalid_request) Missing response_type parameter.'



def get_request(url, params):
    if params:
        query = urllib.urlencode(params)
        request_url = "{}?{}".format(url, query)
    else:
        request_url = url
    print 'request_url', request_url
    res = urllib.urlopen(request_url)
    if res.code == 200:
        return res.read()


class TestWebAuthorize(unittest.TestCase):

    def setUp(self):
        self.url = 'http://127.0.0.1:8000/web/authorize'
        self.client_id = 'b3d127c7-a021-4cb9-aa48-8c77bb06952d'
        self.client_secret = '8c88f283-aff5-4dbf-8980-cbf45a76d0e3'
        self.redirect_uri = 'http://127.0.0.1:5000/callback'
        self.scopes = 'common'
        self.state = 'nothing'
        self.params = {
            'response_type': 'code',
            'client_id': 'b3d127c7-a021-4cb9-aa48-8c77bb06952d',
        }

    def test_missing_client_id(self):
        error_msg = 'invalid_client_id'
        params = {}
        result = get_request(self.url, params)
        self.assertEqual(error_msg, result)

    def test_unvalid_client_id(self):
        error_msg = 'invalid_client_id'
        params = {
            'client_id': 'client_id'
        }
        result = get_request(self.url, params)
        self.assertEqual(error_msg, result)

    def test_missing_response_type(self):
        error_msg = 'invalid_request'
        params = {
            'client_id': 'b3d127c7-a021-4cb9-aa48-8c77bb06952d'
        }
        result = get_request(self.url, params)
        self.assertEqual(error_msg, result)

    def test_unvalid_response_type(self):
        error_msg = 'unauthorized_client'
        self.params.update(response_type='response_type')
        result = get_request(self.url, self.params)
        self.assertEqual(error_msg, result)


    def test_valid_request(self):

        result = get_request(self.url, self.params)
        self.assertTrue('Authorize access to b3d127c7-a021-4cb9-aa48-8c77bb06952d' in result)

    def test_unvalid_redirect_uri(self):
        error_msg = 'invalid_redirect_uri'
        self.params.update(redirect_uri='redirect_uri')
        result = get_request(self.url, self.params)
        self.assertEqual(error_msg, result)

    # def test_unvalid_scopes(self):
    #     self.params.update(scopes='scopes')
    #     result = get_request(self.url, self.params)
    #     self.assertFalse('Authorize access to b3d127c7-a021-4cb9-aa48-8c77bb06952d' in result)






if __name__ == '__main__':
    unittest.main()

