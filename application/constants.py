#!/usr/bin/env python
# -*- coding:utf8 -*-
from gettext import gettext as _

class APIStatusCode(object):
    OK = 0
    Unknown = 500


class APIStatus(object):
    def __init__(self, code, memo):
        self.code = code
        self.memo = memo

    def marshal(self):
        return {
            'code': int(self.code),
            'memo': self.memo,
        }


API_STATUS_OK = APIStatus(code=APIStatusCode.OK, memo=_('API_STATUS_OK'))
API_STATUS_UNKNOWN = APIStatus(code=APIStatusCode.Unknown, memo=_('API_STATUS_UNKNOWN'))
