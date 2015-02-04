#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import datetime
import base64
import logging
from oauthlib.oauth2 import RequestValidator
from .models import Client, BearerToken, User
from app.utils import genera_expires_time

logger = logging.getLogger('oauth')


class LegacyValidator(RequestValidator):
    def authenticate_client(self, request, *args, **kwargs):

        logger.info('验证客户端')

        authorization = request.headers.get('Authorization')
        access_token_b64 = authorization[6:]
        client_id, client_secret = base64.b64decode(access_token_b64).split(':')

        try:
            client = Client.objects.get(client_id=client_id, client_secret=client_secret)
        except:
            return False
        setattr(request, 'client', client)
        request._client = client
        return True

    def validate_user(self, username, password, client, request, *args, **kwargs):
        logger.info('验证用户名和密码')
        user = User.objects(username=username, password=password)
        if not user:
            return False
        request._user = user
        return True

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        logger.info('验证 grant_type 类型')
        try:
            grant_type = dict(map(lambda x: x.split('='), request.body.split('&'))).get('grant_type')
            if grant_type == 'password' or grant_type == 'refresh_token':
                return True
        except:
            return False

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        return request._client.default_scopes

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        if not request._client.scopes:
            request._client.scopes = self.get_default_scopes(client_id, request)
            request._client.save()
        return all(map(lambda s: s in request._client.scopes, scopes))

    def save_bearer_token(self, token, request, *args, **kwargs):
        logger.info('生成 token')
        access_token = token.get('access_token')
        refresh_token = token.get('refresh_token')
        expires_in = token.get('expires_in')
        expires_at = genera_expires_time(minutes=expires_in)
        # 授权之后生成 access_token
        if request._user:
            bt = BearerToken.objects(client=request._client, user=request._user[0]).first()
            if bt:
                bt.delete()
            data = dict(
                client=request._client,
                user=request._user[0],
                scopes=request._client.scopes,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at
            )
            try:
                bt = BearerToken(**data)
                bt.save()
            except Exception, e:
                print e
        # refresh 更新保存 access_token
        else:
            request._bearertoken.expires_at = expires_at
            request._bearertoken.access_token = token.get('access_token')
            request._bearertoken.refresh_token = token.get('refresh_token')
            request._bearertoken.save()

    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):

        logger.info('验证 refresh_token')

        try:
            bt = BearerToken.objects.get(refresh_token=refresh_token, client=client)
        except BearerToken.DoesNotExist, e:
            return False
        request._bearertoken = bt
        return True

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):

        bt = BearerToken.objects(refresh_token=refresh_token).first()
        return bt.scopes

    def validate_bearer_token(self, token, scopes, request):
        logger.info('验证访问资源的 access_token')
        authorization = request.headers.get('Authorization')
        access_token_b64 = authorization[7:]
        access_token = base64.b64decode(access_token_b64)
        now = datetime.datetime.utcnow()
        try:
            bt = BearerToken.objects.get(access_token=access_token, expires_at__gte=now)
            # TODO validate the scopes
            # author_scopes = bt.scopes.split()

        except:
            return False
        request.user = bt.user
        return True

