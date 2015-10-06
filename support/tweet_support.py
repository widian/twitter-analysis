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

if __name__ == '__main__':
    pass
