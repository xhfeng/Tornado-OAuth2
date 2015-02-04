#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import logging
import tornado.httpserver
import tornado.ioloop
from mongoengine import connect

from app import Application
from settings import config


def create_app():
    app = Application()
    return app

def create_db():

    connect(
        db=config.MONGODB['db'],
        username=config.MONGODB['username'],
        password=config.MONGODB['password'],
        host=config.MONGODB['host'],
        port=config.MONGODB['port']
    )


def create_log():
    logger = logging.getLogger('oauth2')
    logger.setLevel(logging.DEBUG)


    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)



if __name__ == '__main__':

    app = create_app()
    create_db()
    create_log()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(config.PORT)
    io_loop = tornado.ioloop.IOLoop.instance()
    io_loop.start()


