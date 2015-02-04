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
    grant_type = StringField(max_length=18, default='password',
                             choices=[('password', 'Password')])
    scopes = StringField()
    default_scopes = StringField(default='common')

    def __repr__(self):
        return '<Client %s>' % self.client_id

    @classmethod
    def client(cls):
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

    connect(
        'tornado-oauth2',
        username='',
        password='',
        host='localhost',
        port=27017
    )

