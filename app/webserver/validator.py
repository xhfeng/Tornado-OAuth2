#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import datetime
import base64
from oauthlib.oauth2 import RequestValidator
from .models import Client, AuthorizationCode, BearerToken
from app.utils import genera_expires_time


class WebValidator(RequestValidator):
    """
    OAuth2 验证接口。
    验证客户端的合法性
    保存 code，access_token, refresh_token
    验证 code，access_token, refresh_token
    """

    def validate_client_id(self, client_id, request, *args, **kwargs):
        """
        验证客户端的合法性，发生在客户端授权的时候认证

        :param client_id: 客户端发起的 url 中的 client_id
        :param request: 客户端发起的请求对象
        :return: 合法返回 True，非法返回 False
        """

        try:
            request._client = Client.objects.get(client_id=client_id)
            return True
        except:
            return False


    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        """
        验证客户端申请的 redirect_uri 地址

        :param client_id: 客户端发起的 url 中的 client_id
        :param redirect_uri:  客户端发起的 url 中的 redirect_uri
        :param request: 客户端发起的请求对象
        :return: 合法的redirect_uri，验证通过，返回 True，反之 False
        """
        if request._client.redirect_uris == redirect_uri:
            return True
        return False


    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        """
        获取默认的 redirect_uri

        :param client_id: 客户端发起的 url 中的 client_id
        :param request: 客户端发起的请求对象
        :return: 返回默认的 redirect_uri
        """
        return request._client.default_redirect_uri

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        """
        验证授权的范围，如果url的 scopes 为空，则自动调用 get_default_scopes 返回系统默认的scopes赋值给scopes
        如果 系统的 scopes 为空，则手动调用 get_default_scopes 给系统的 scopes 赋值

        :param client_id: 客户端发起的 url 中的 client_id
        :param scopes: 客户端发起的 url 中的 scopes
        :param client: 客户端 client 对象
        :param request: 客户端发起的请求对象
        :return: 验证通过返回 True，反之 False
        """

        print scopes

        if not request._client.scopes:
            request._client.scopes = self.get_default_scopes(client_id, request)
            request._client.save()
        return all(map(lambda s: s in request._client.scopes, scopes))


    def get_default_scopes(self, client_id, request, *args, **kwargs):
        """
        返回系统默认的 scopes

        :param client_id: 客户端发起的 url 中的 client_id
        :param request: 客户端 client 对象
        :return: 返回系统默认的 scopes
        """
        return request._client.default_scopes


    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        if request._client.response_type == response_type:
            return True
        return False


    # Post-authorization
    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        """
        将生成的 authorization code 保存到数据库，设定过期时间

        :param client_id: 客户端发起的 url 中的 client_id:
        :param code: 验证通过生成的 code 对象
        """

        user = request.user[0]
        scopes = request._client.scopes
        code = code.get('code')
        expires_at = genera_expires_time(minutes=10)
        try:
            ac = AuthorizationCode(client=request._client, user=user, scopes=scopes, code=code, expires_at=expires_at)
            ac.save()
        except Exception, e:
            raise e


    # Token request
    def authenticate_client(self, request, *args, **kwargs):
        """
        验证客户端合法性，发生在通过code请求token的阶段。 验证 headers 的 basic， base64(client_id:client_secret)
        :param request: 客户端 post 请求
        :return: 合法返回 True, 非法返回 Fasle 错误信息为 invalid_client
        """
        # Todo Headers validate Basic
        headers = request.headers
        try:
            client = Client.objects.get(client_id=request.client_id)
        except:
            return False
        setattr(request, 'client', client)
        self._client = client
        return True


    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        # Don't allow public (non-authenticated) clients
        return False


    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        """
        验证客户端的 grant_type， 只能取值为 authorization_code， refresh_token

        :param grant_type:  客户端 post 的 grant_type 值
        :return: 验证通过返回 True，不通过则返回False 错误信息 unauthorized_client
        """
        try:
            grant_type = dict(map(lambda x: x.split('='), request.body.split('&'))).get('grant_type')
            if grant_type == 'authorization_code' or grant_type == 'refresh_token':
                return True
        except:
            return False


    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        """
        验证客户端用户授权的 code， code 是 unicode, 验证的code时间不能超过code的过期时间

        :param code:  request 请求的 code
        :return:

        """

        now = datetime.datetime.utcnow()
        try:
            ac = AuthorizationCode.objects.get(code=code, expires_at__gte=now)
        except:
            return False
        self._authorizationcode = ac
        return True


    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, *args, **kwargs):
        """
        验证 post 的 redirect_uri 与 client 注册的是否一致

        :param redirect_uri: 客户端 post 的 redirect_uri
        :return: 验证通过返回 True
        """
        if self._client.redirect_uris == redirect_uri:
            return True
        return False


    def save_bearer_token(self, token, request, *args, **kwargs):
        """
        保存验证通过的 access_token 和 refresh_token
        该方法出现在两个情景：
        * 通过 code 换取 access_token，，如果重新授权，则删除旧的记录，新增记录
        * 通过 refresh_token 重新获取 access_token，则更新记录

        :param token:  验证通过生成的 token 字典
        """

        access_token=token.get('access_token')
        refresh_token=token.get('refresh_token')
        expires_in = token.get('expires_in')
        expires_at = genera_expires_time(minutes=expires_in)

        # code 获取 access_token
        if hasattr(self, '_authorizationcode'):
            bt = BearerToken.objects(client=self._client, user=self._authorizationcode.user).first()
            if bt:
                bt.delete()
            data = dict(
                client = self._client,
                user=self._authorizationcode.user,
                scopes=self._authorizationcode.scopes,
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

            self._bearertoken.expires_at = expires_at
            self._bearertoken.access_token = token.get('access_token')
            self._bearertoken.refresh_token = token.get('refresh_token')
            self._bearertoken.save()

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        """
        code 使用之后，说明用户授权了，然后需要把这个 code 变成无效，code 只能一次性换取 access token

        :param code: 验证授权通过的 code
        """

        AuthorizationCode.objects.get(code=code).delete()


    # Protected resource request
    def validate_bearer_token(self, token, scopes, request):
        """
        验证 access_token 的合法性，token 在 request的 headers， 用户通过 headers 发送 access_token

        curl -X GET -H "Bearer vwqhj7AnsVCW1LxwFt0fV2yKpg34Fb" http://example.com/protect

        :param scopes: 默认的访问范围
        :return: 403 禁止客户端访问
        """

        authorization = request.headers.get('Authorization')
        access_token_b64 = authorization[7:]
        access_token = base64.b64decode(access_token_b64)

        # access_token = request.headers.get('Bearer')
        now = datetime.datetime.utcnow()

        try:
            bt = BearerToken.objects.get(access_token=access_token, expires_at__gte=now)
        except:
            return False
        request.user = bt.user
        return True


    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        """
        验证 refresh_token 是否合法
        :param refresh_token:
        :return: 错误信息 invalid_grant， 表示非法的 refresh_token
        """
        try:
            bt =  BearerToken.objects.get(refresh_token=refresh_token, client=client)
        except BearerToken.DoesNotExist, e:
            return False
        self._bearertoken = bt
        return True

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        """
        获取默认的 scopes

        :param refresh_token:
        :return: 返回 BearerToken 记录的用户授权的访问范围
        """
        bt = BearerToken.objects(refresh_token=refresh_token).first()
        return bt.scopes

