#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import functools
import tornado.web
from oauthlib.oauth2 import WebApplicationServer
from app.utils import extract_params
from .validator import LegacyValidator


class LegacyProviderDecorator(object):
    def __init__(self):
        super(LegacyProviderDecorator, self).__init__()
        validator = LegacyValidator()
        self._resource_endpoint = WebApplicationServer(validator)

    def protected_resource_view(self, scopes=None):
        def decorator(f):
            @functools.wraps(f)
            def wrapper(request, *args, **kwargs):
                try:
                    scopes_list = scopes(request)
                except TypeError:
                    scopes_list = scopes

                uri, http_method, body, headers = extract_params(request)

                valid, r = self._resource_endpoint.verify_request(
                    uri, http_method, body, headers, scopes_list)

                kwargs.update({
                    'client': r.client,
                    'user': r.user,
                    'scopes': r.scopes
                })
                if valid:
                    request.request.current_user = kwargs.get('user')
                    return f(request, *args, **kwargs)
                else:
                    raise tornado.web.HTTPError(403)

            return wrapper

        return decorator


provider = LegacyProviderDecorator()
