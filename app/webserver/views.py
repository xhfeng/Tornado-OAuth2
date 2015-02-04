#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import logging
import uuid
import tornado.web
import tornado.httpclient
from app import router
from app.utils import extract_params
from oauthlib.oauth2 import WebApplicationServer
from oauthlib.oauth2.rfc6749 import errors
from .validator import WebValidator
from .models import Client
from .decorator import provider


logger = logging.getLogger('web')


@router.Route('/web/authorize', name='web-authorize')
class WebAuthorizeHandler(tornado.web.RequestHandler):
    """
    oauth 用户授权
    """

    def initialize(self):
        # 初始化 oauth2 后端服务
        self._authorization_endpoint = WebApplicationServer(WebValidator())
        self._error_uri = self.reverse_url('web-error')

    def get(self):
        # 解析 request，包装 oauthlib request
        uri, http_method, body, headers = extract_params(self.request)
        redirect_uri = self.get_query_argument('redirect_uri', None)

        try:
            # 验证client请求，识别client身份
            scopes, credentials = self._authorization_endpoint.validate_authorization_request(
                uri, http_method, body, headers)
        except errors.FatalClientError as e:
            logger.error(e.error)
            self.finish(e.error)
            self.redirect(self._error_uri)
        except errors.OAuth2Error as e:
            e.redirect_uri = redirect_uri
            logger.error(e.error)
            self.finish(e.error)
            self.redirect(e.in_uri(e.redirect_uri))

        # 渲染用户认证授权页面
        self.write('<h1> Authorize access to %s </h1>' % credentials['client_id'])
        self.write('<form method="POST" action="">')
        for scope in scopes or []:
            self.write('<input type="checkbox" checked="checked" name="scopes" value="%s"/> %s' % (scope, scope))

        self.write('<input type="text" name="username" value="username"/>')
        self.write('<input type="password" name="password" value="password"/>')
        self.write('<input type="submit" value="Authorize"/>')


    def post(self, *args, **kwargs):
        uri, http_method, body, headers = extract_params(self.request)

        try:
            headers, body, status = self._token_endpoint.create_token_response(uri, http_method, body, headers)

        except errors.FatalClientError as e:
            logger.error(e)
            print e
            self.redirect(self._error_uri)
        except errors.OAuth2Error as e:
            logger.error(e)
            print e
            self.redirect(self._error_uri)

        self.set_header('Content-Type', 'application/json')
        self.finish(body)


@router.Route('/web/refresh', name='web-refresh')
class WebRefreshHandler(tornado.web.RequestHandler):
    def initialize(self):
        # 初始化 oauth2 后端服务
        self._refresh_endpoint = WebApplicationServer(WebValidator())
        self._error_uri = self.reverse_url('web-error')

    def post(self, *args, **kwargs):
        uri, http_method, body, headers = extract_params(self.request)

        try:
            headers, body, status = self._refresh_endpoint.create_token_response(
                uri, http_method, body, headers)
        except errors.FatalClientError as e:
            logger.error(e)
            self.redirect(self._error_uri)
        except errors.OAuth2Error as e:
            logger.error(e)
            self.redirect(self._error_uri)
        self.set_header('Content-Type', 'application/json')
        self.finish(body)


@router.Route('/web', name='web-index')
class WebIndexHandler(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        self.write('hello world')

@router.Route('/web/protect', name='web-protect')
class WebProtectHandler(tornado.web.RequestHandler):

    @provider.protected_resource_view(scopes=['common', 'email'])
    def get(self, *args, **kwargs):
        self.write('<h1>hello %s </h1>' % self.request.current_user.username)
        self.write('<p>this is protect resource</p>')

@router.Route('/web/error/', name='web-error')
class WebErrorHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('error')


@router.Route('/web/client')
class WebClientHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):

        clients = Client.objects()
        self.render('webserver/client.html', clients=clients)


    def post(self, *args, **kwargs):

        client_id = str(uuid.uuid4())
        client_secret = str(uuid.uuid4())

        try:
            client = Client(client_id=client_id, client_secret=client_secret)
            client.save()
        except Exception, e:
            self.finish('client generator error')
            return

        result = dict(
            client_id=client_id,
            client_secret=client_secret,
            grant_type=client.grant_type,
            scopes=client.scopes,
            default_scopes=client.default_scopes
        )

        self.write(result)



