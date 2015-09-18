#!/usr/bin/env python
# -*- coding:utf8 -*-
from gettext import gettext as _

class APIStatusCode(object):
    OK = 200
    rate_limit = 429
    unknown = 500
    on_twitter_search = 1001
    already_refreshed = 1002
    uncaught_required = 1003

class APIStatus(object):
    def __init__(self, code, memo):
        self.code = code
        self.memo = memo

    def marshal(self):
        return {
            'code': int(self.code),
            'memo': self.memo,
        }

API_STATUS_OK = APIStatus(code=APIStatusCode.OK , memo=_('API_STATUS_OK'))
API_STATUS_UNKNOWN = APIStatus(code=APIStatusCode.unknown, memo=_('API_STATUS_UNKNOWN'))
API_STATUS_RATE_LIMIT = APIStatus(code=APIStatusCode.rate_limit, memo=_('API_STATUS_RATE_LIMIT'))
API_STATUS_ON_TWITTER_SEARCH = APIStatus(code=APIStatusCode.on_twitter_search, memo=_('API_STATUS_ON_TWITTER_SEARCH'))
API_STATUS_ALREADY_REFRESHED = APIStatus(code=APIStatusCode.already_refreshed, memo=_('API_STATUS_ALREADY_REFRESHED'))
API_STATUS_UNCAUGHT_REQUIRED = APIStatus(code=APIStatusCode.uncaught_required, memo=_('API_STATUS_UNCAUGHT_REQUIRED'))
