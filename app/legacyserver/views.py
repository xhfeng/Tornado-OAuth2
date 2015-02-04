#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'


import tornado.web
from app import router

@router.Route('/legacy', name='legacy')
class LegacyIndexHandler(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        self.write('hello world')

