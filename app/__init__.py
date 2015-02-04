#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import tornado.web
from app.legacyserver.views import *
from app import router
from settings import config




class Application(tornado.web.Application):
    def __init__(self):
        super(Application, self).__init__(
            handlers=router.Route.get_routes(),
            **config.SETTINGS
        )

    print 'Server %s start listening %s' % (config.DEPLOY, config.PORT)
