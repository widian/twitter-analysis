#!/usr/bin/env python
# -*- coding:utf8 -*-
import os
from flask import Flask
from TwitterSearch import *
import datetime
from blueprint import APIBlueprint
from constants import API_STATUS_OK, API_STATUS_UNKNOWN

class MyTwitterSearchOrder(TwitterSearchOrder):
    def set_since(self, date):
        """ Sets 'since' parameter used to return \
        only tweets generated after the given date

        :param date : A datetime instance
        :raises: TwitterSearchException
        """

        if isinstance(date, datetime.date) and date <= datetime.date.today():
            self.arguments.update({'since': '%s' % date.strftime('%Y-%m-%d')})
        else:
            raise TwitterSearchException(1007)

api_bp = APIBlueprint('api', __name__, url_prefix='/api')
@api_bp.route('/twit', methods=['GET'])
def get_twit():
    try:
        tso = MyTwitterSearchOrder()
        #tso = TwitterUserOrder('lys2419') # create a TwitterUserOrder to access specific user timeline
        tso.set_keywords(['미오'])
        tso.set_language('ko')
        tso.set_include_entities(False)
        today = datetime.datetime.utcnow().date()
        tso.set_since(today - datetime.timedelta(days=1))
        tso.set_until(today - datetime.timedelta(days=0))

        ts = TwitterSearch(
                consumer_key = 'Jn0vFPTkewSek85vb1USoCQf4',
                consumer_secret = 'VnFh6AvyiojNKVFUryQXWaKKzHsvBsVnebjQWDcOCfftsjgO9J',
                access_token = '100506002-67IOcA0mZehNVmJlqmkOIB4QsJfjlXKK1OX0ylqO',
                access_token_secret = 'j72a7volEPzuwRAmu44j467IyxdZHpgIA1fPxU6AgWDy1')
        for tweet in ts.search_tweets_iterable(tso):
            tweet_text = ('%s @%s tweeted: %s' % (tweet['created_at'], tweet['user']['screen_name'], tweet['text']))
        return api_bp.make_response(status=API_STATUS_OK, result=dict())
    except TwitterSearchException as e:
        print e
        return api_bp.make_response(status=API_STATUS_UNKNOWN, result=dict())

