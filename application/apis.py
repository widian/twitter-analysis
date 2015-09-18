#!/usr/bin/env python
# -*- coding:utf8 -*-
import os
import datetime

from flask import Flask, request
from blueprint import APIBlueprint
from constants import API_STATUS_OK, API_STATUS_UNKNOWN, API_STATUS_RATE_LIMIT, API_STATUS_ON_TWITTER_SEARCH

from TwitterSearch import TwitterSearchException

from keen_support import Keen
from tweet_support import TweetSearchSupport
import redis_support
import charcollection

api_bp = APIBlueprint('api', __name__, url_prefix='/api')
@api_bp.route('/get_twit', methods=['GET'])
def get_twit():
    target_character_number = request.args.get("character")
    target_collection_number = request.args.get("collection")
    if target_collection_number is None or target_character_number is None:
        return api_bp.make_response(status=API_STATUS_UNKNOWN, result = {"result" : False})
    if redis_support.exist_lock_twitter_search():
        # On Twitter search caused rate limit
        return api_bp.make_response(status=API_STATUS_RATE_LIMIT, result = {"result" : False, "ttl" : redis_support.ttl_exist_lock_twitter_search()})
    try:
        today = datetime.datetime.now().date()
        tss = TweetSearchSupport()
        ts = tss.get_ts()
        keen = Keen()

        # LOCK twitter search using redis
        if redis_support.lock_twitter_search():
            # On Twitter search error
            return api_bp.make_response(status=API_STATUS_ON_TWITTER_SEARCH, result = {"result" : False})

        character = charcollection.get_character(target_collection_number, target_character_number)
        if character == False:
            return api_bp.make_response(status=API_STATUS_UNKNOWN, result = {"result" : False})
        collection = charcollection.get_collection(target_collection_number)
        if collection == False:
            return api_bp.make_response(status=API_STATUS_UNKNOWN, result = {"result" : False})

        tso = tss.generate_tso(character, today)
        count_dict = dict()
        amount = 0
        for tweet in ts.search_tweets_iterable(tso):
            tweet_create_date = tss.to_datetime(tweet['created_at']).date()
            timestamp = tweet_create_date.strftime("%Y-%m-%dT03:00:00.000Z")
            if not count_dict.has_key(timestamp):
                count_dict[timestamp] = 1
            else:
                count_dict[timestamp] += 1
        redis_support.unlock_twitter_search()
        # UNLOCK twitter search

        keen.add_girl(collection, character, count_dict)
        return api_bp.make_response(status=API_STATUS_OK, result={ "result" : True })
    except TwitterSearchException as e:
        if e.code == 429:
            # On Twitter search caused rate limit
            redis_support.expire_lock_twitter_search()
            return api_bp.make_response(status=API_STATUS_RATE_LIMIT, result={"result" : False, "ttl" : redis_support.ttl_exist_lock_twitter_search()})
        else:
            print e
            return api_bp.make_response(status=API_STATUS_UNKNOWN, result=dict())

@api_bp.route('/add_event', methods=['GET'])
def add_event():
    redis_support.redis_set("test", False)
    print redis_support.redis_get("test")
    return api_bp.make_response(status=API_STATUS_OK, result={"result" : redis_support.redis_get("test")})

