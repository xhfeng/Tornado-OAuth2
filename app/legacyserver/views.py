#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import uuid
import logging
import tornado.web
from oauthlib.oauth2 import LegacyApplicationServer
from oauthlib.oauth2.rfc6749 import errors
from app import router
from app.utils import extract_params
from .validator import LegacyValidator
from .models import Client
from .decorator import provider


logger = logging.getLogger('legacy')


@router.Route('/legacy', name='legacy')
class LegacyIndexHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write('hello legacy')


@router.Route('/legacy/authorize', name='legacy-authorize')
class LegacyAuthorizeHandler(tornado.web.RequestHandler):
    def initialize(self):
        self._token_endpoint = LegacyApplicationServer(LegacyValidator())
        self._error_uri = self.reverse_url('legacy-error')

    def post(self, *args, **kwargs):
        uri, http_method, body, headers = extract_params(self.request)

        try:
            headers, body, status = self._token_endpoint.create_token_response(uri, http_method, body, headers)
        except errors.FatalClientError as e:
            logger.error(e)
            self.redirect(self._error_uri)
        except errors.OAuth2Error as e:
            logger.error(e)
            self.redirect(self._error_uri)

        self.set_header('Content-Type', 'application/json')
        self.finish(body)


@router.Route('/legacy/refresh', name='legacy-refresh')
class LegacyRefreshHandler(tornado.web.RequestHandler):
    def initialize(self):
        # 初始化 oauth2 后端服务
        self._refresh_endpoint = LegacyApplicationServer(LegacyValidator())
        self._error_uri = self.reverse_url('legacy-error')

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


@router.Route('/legacy/protect', name='legacy-protect')
class OauthProtectHandler(tornado.web.RequestHandler):
    @provider.protected_resource_view(scopes=['common', 'email'])
    def get(self, *args, **kwargs):
        self.write('<h1>hello %s </h1>' % self.request.current_user.username)
        self.write('<p>this is protect resource</p>')


@router.Route('/legacy/error', name='legacy-error')
class LegacyErrorHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('legacy error')


@router.Route('/legacy/client')
class LegacyClientHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):

        clients = Client.objects()
        self.render('legacy/client.html', clients=clients)


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
