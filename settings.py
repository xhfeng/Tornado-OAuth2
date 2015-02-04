#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'


import tornado.util
from tornado.options import define, options


define('env', default='dev')
options.parse_command_line()


if options.env == 'dev':
    config = tornado.util.import_object('config.dev')
elif options.env == 'pro':
    config = tornado.util.import_object('config.pro')
