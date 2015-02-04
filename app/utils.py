#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import datetime
import urlparse
import base64
from tornado.httputil import HTTPServerRequest


def extract_params(request):

    if not isinstance(request, HTTPServerRequest):
        request = request.request

    parse_url = urlparse.urlparse(request.uri)
    path, params, query, fragment = parse_url.path, parse_url.params, parse_url.query, parse_url.fragment
    uri = urlparse.urlunparse((request.protocol, request.host, path, params, query, fragment))

    http_method = request.method
    headers = request.headers
    if 'wsgi.input' in headers:
        del headers['wsgi.input']
    if 'wsgi.errors' in headers:
        del headers['wsgi.errors']
    if 'HTTP_AUTHORIZATION' in headers:
        headers['Authorization'] = headers['HTTP_AUTHORIZATION']

    body = request.body
    # if body:
    #     body = map(lambda x: x.split('='), request.body.split('&'))
    #     body = urllib.urlencode(map(lambda x: tuple(x), body))

    return uri, http_method, body, headers



def genera_expires_time(**kwargs):

    now = datetime.datetime.utcnow()
    save_time = now + datetime.timedelta(**kwargs)
    return save_time
