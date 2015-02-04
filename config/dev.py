#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import os


DEPLOY = 'development'

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

SETTINGS = {
    "debug": True,
    "template_path": os.path.join(PROJECT_ROOT, "templates"),
    "static_path": os.path.join(PROJECT_ROOT, "static"),
    "cookie_secret": "YXRvbS50cmFkZSBpcyB0aGUgYmVzdAo=",
    "login_url": "/login"
}

PORT = 8000

MONGODB = {
    'db': 'tornado-oauth2',
    'username': '',
    'password': '',
    'host': 'localhost',
    'port': 27017
}
