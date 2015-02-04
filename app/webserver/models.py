#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import datetime
import mongoengine
from mongoengine import *


class User(Document):
    username = StringField()
    password = StringField()
    created_at = DateTimeField(default=datetime.datetime.now)

    def __repr__(self):
        return '<User %s>' % self.username

    @classmethod
    def user(cls):
        return cls.objects._collection


class Client(Document):
    client_id = StringField(max_length=100, required=True)
    client_secret = StringField(max_length=100, required=True)
    grant_type = StringField(max_length=18, default='authorization_code',
                             choices=[('authorization_code', 'Authorization code')])
    response_type = StringField(max_length=4, default='code', choices=[('code', 'Authorization code')])
    scopes = StringField()
    default_scopes = StringField(default='common')
    redirect_uris = StringField()
    default_redirect_uri = StringField(default='http://127.0.0.1:5000/callback')

    def __repr__(self):
        return '<Client %s>' % self.client_id

    @classmethod
    def client(cls):
        return cls.objects._collection


class AuthorizationCode(Document):
    client = ReferenceField(Client, reverse_delete_rule=mongoengine.NULLIFY)
    user = ReferenceField(User, reverse_delete_rule=mongoengine.NULLIFY)
    scopes = StringField()
    code = StringField(max_length=100, unique=True)
    expires_at = DateTimeField()

    def __repr__(self):
        return '<AuthorizationCode %s>' % self.code

    @classmethod
    def authorizationcode(cls):
        return cls.objects._collection


class BearerToken(Document):
    client = ReferenceField(Client, reverse_delete_rule=mongoengine.NULLIFY)
    user = ReferenceField(User, reverse_delete_rule=mongoengine.NULLIFY)
    scopes = StringField()
    access_token = StringField(max_length=100, unique=True)
    refresh_token = StringField(max_length=100, unique=True)
    expires_at = DateTimeField()

    def __repr__(self):
        return '<BearerToken %s>' % self.access_token

    @classmethod
    def bearertoken(cls):
        return cls.objects._collection


if __name__ == '__main__':
    from mongoengine import connect

    db = connect(
        'tornado-oauth2',
        username='',
        password='',
        host='localhost',
        port=27017
    )
