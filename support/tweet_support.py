#!/usr/bin/env python
# -*- coding:utf8 -*-
import twitter

try:
    from config import CONSUMER_KEY
    from config import CONSUMER_SECRET
    from config import ACCESS_TOKEN_KEY
    from config import ACCESS_TOKEN_SECRET
except:
    print 'Tweet API keys are not exist'
    exit()

class TweetSupport(object):
    api = None
    def __init__(self, sleep_on_rate_limit=False):
        self.api = twitter.Api(
                consumer_key=CONSUMER_KEY,
                consumer_secret = CONSUMER_SECRET,
                access_token_key = ACCESS_TOKEN_KEY,
                access_token_secret=ACCESS_TOKEN_SECRET)
    def get_api(self):
        return self.api

class TweetErrorNumber(object):
    RATE_LIMIT_ERROR = 88
    NOT_AUTHORIZED = u'Not authorized.'

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
            return dict() 
        else:
            """ error container is list"""
        result = dict()
        for case in self.error_container:
            if not isinstance(case, dict):
                if self.error_container in self.error_handler:
                    new_case = self.error_container
                    result[new_case] = self.error_handler[new_case](new_case, **kwargs)
                    break
                else:
                    print case, 
                    continue
            if case['code'] in self.error_handler:
                result[case['code']] = self.error_handler[case['code']](case, **kwargs)
            else:
                self.default_handler(case, **kwargs)
        return result

    def default_error_handler(self, case, **kwargs):
        print case['message']

ErrorNumbers = TweetErrorNumber()

if __name__ == '__main__':
    pass
