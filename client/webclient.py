#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import urllib
import urllib2
import tornado.web
import tornado.httpserver
import tornado.ioloop


class CallbackHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        query = self.request.uri[2:]
        code = dict(map(lambda x: x.split('='), query.split('&'))).get('code')

        params = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'http://127.0.0.1:5000/callback',
            'client_id': '1f06993e-8c1a-4963-96b2-1e280652b4cb'
        }

        url = 'http://127.0.0.1:8000/web/token'
        data = urllib.urlencode(params)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        if response.code == 200:
            tokeninfo = response.read()
            return self.write(tokeninfo)


class AuthorizeHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write(
            '<a href="http://127.0.0.1:8000/web/authorize?client_id=1f06993e-8c1a-4963-96b2-1e280652b4cb&response_type'
            '=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000">用户授权</a>')


class HomeHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        """
        http://127.0.0.1:5000?access_token=dsadasdasdas
        """
        print self.request.uri

        access_token = self.request.uri[6:].split('=')[1]

        request = urllib2.Request('http://127.0.0.1:8000/web/protect')
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1')
        request.add_header('Accept-Charset', 'GBK,utf-8;q=0.7,*;q=0.3')
        request.add_header('Bearer', '%s' % access_token,)
        response = urllib2.urlopen(request)
        return self.write(response.read())


app = tornado.web.Application(
    handlers=[
        (r'/callback', CallbackHandler),
        (r'/authorize', AuthorizeHandler),
        # (r'/home', HomeHandler),
    ]
    , debug=True)

if __name__ == '__main__':
    server = tornado.httpserver.HTTPServer(app)
    server.listen(5000)
    tornado.ioloop.IOLoop.instance().start()

