#!/usr/bin/env python
# -*- coding:utf8 -*-
import twitter

class TweetSupport(object):
    api = None
    def __init__(self):
        self.api = twitter.Api(
                consumer_key= 'Jn0vFPTkewSek85vb1USoCQf4',
                consumer_secret = 'VnFh6AvyiojNKVFUryQXWaKKzHsvBsVnebjQWDcOCfftsjgO9J',
                access_token_key = '100506002-67IOcA0mZehNVmJlqmkOIB4QsJfjlXKK1OX0ylqO',
                access_token_secret='j72a7volEPzuwRAmu44j467IyxdZHpgIA1fPxU6AgWDy1')
    def get_api(self):
        return self.api

class TweetErrorHandler(object):
    error_container = None
    error_handler = dict()
    default_handler = None
    def __init__(self, e):
        """ e : TwitterError 
            caught in try-except routine about twitter api.
        """
        self.error_container = e.message
        self.default_handler = self.default_error_handler

    def add_handler(self, code, action):
        """ code : number
            action : lambda x
        """
        self.error_handler[code] = action
        return True

    def invoke(self, **kwargs):
        if self.error_container is None:
            print "Error didn't bind to container"
            return False
        else:
            """ error container is list"""
        for case in self.error_container:
            if case['code'] in self.error_handler:
                self.error_handler[case['code']](case, **kwargs)
            else:
                self.default_handler(case, **kwargs)

    def default_error_handler(self, case, **kwargs):
        print case['message']


if __name__ == '__main__':
    pass
