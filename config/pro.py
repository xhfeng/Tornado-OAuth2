#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import os


DEPLOY = 'production'

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

SETTINGS = {
    "debug": False,
    "template_path": os.path.join(PROJECT_ROOT, "templates"),
    "static_path": os.path.join(PROJECT_ROOT, "static"),
    "cookie_secret": "YXRvbS50cmFkZSBpcyB0aGUgYmVzdAo=",
    "login_url": "/login"
}

PORT = 9999

MONGODB = {
    'db': '',
    'username': '',
    'password': '',
    'host': '',
    'port': 27017
}


