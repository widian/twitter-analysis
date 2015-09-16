#!/usr/bin/env python
# -*- coding:utf8 -*-
import os
from flask import Flask
from TwitterSearch import *
import datetime
from blueprint import APIBlueprint
from constants import API_STATUS_OK, API_STATUS_UNKNOWN
from keen.client import KeenClient
keen_client = KeenClient(
        project_id="55f93f85d2eaaa05a699de39",
        write_key="8f77f837b629b8519e8d23c541fedc42d423f8f71dc10e2244b50e364e7034cb753d960ea31d7925d044a109233cdf55e88792d4fa9f16f4e2410a7e09309242565415ef3d7299526c2fbf6860603bd349d186f068f5bd940ff047c2f4a4f0959c1cda4c3c3208729524b233b096e4de",
        read_key="2f1b89a70f545caaeff7964b5daa60236844aa0291a20749e15ca83e30c63d3cb939d7eb720666c03164403680d77d8e6086e3f1d60b5a34f696b09fc1bd695a0a0f0a1f947757cd5bd5666d5448b614e9928a544bfcecfe4bb9e52b1c02d77e49e359c04dc2dd901764097364b00573",
        master_key="3855C83BD7B0720323E0B1E447149B01")


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
        tso.set_keywords(['시부야 린'])
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

        #ts.search_tweets(tso)
        for tweet in ts.search_tweets_iterable(tso):
            tweet_text = ('%s @%s tweeted: %s' % (tweet['created_at'], tweet['user']['screen_name'], tweet['text']))


        return api_bp.make_response(status=API_STATUS_OK, result=dict(
            amount=ts.get_amount_of_tweets()))
    except TwitterSearchException as e:
        print e
        return api_bp.make_response(status=API_STATUS_UNKNOWN, result=dict())

@api_bp.route('/add_event', methods=['GET'])
def add_event():
    keen_client.add_events({
        "test_cases" : [
            {"user_name" : "nameuser4",
             "count" : 4 
            },
            {"user_name" : "nameuser5",
                "count" : 5}]
    })
    return api_bp.make_response(status=API_STATUS_OK, result=dict(
        event_amount=keen_client.count("sign_ups", timeframe="this_14_days")))

