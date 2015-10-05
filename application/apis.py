#!/usr/bin/env python
# -*- coding:utf8 -*-
import os
import datetime

from flask import Flask, request
from blueprint import APIBlueprint
from constants import API_STATUS_OK, API_STATUS_UNKNOWN, API_STATUS_RATE_LIMIT, API_STATUS_ON_TWITTER_SEARCH, API_STATUS_ALREADY_REFRESHED, API_STATUS_UNCAUGHT_REQUIRED

from TwitterSearch import TwitterSearchException

from keen_support import Keen
from tweet_support import TweetSearchSupport
import redis_support
import charcollection

api_bp = APIBlueprint('api', __name__, url_prefix='/api')
@api_bp.route('/get_twit', methods=['GET'])
def get_twit():
    target_character_number = int(request.args.get("character"))
    target_collection_number = int(request.args.get("collection"))
    if target_collection_number is None or target_character_number is None:
        return api_bp.make_response(status=API_STATUS_UNCAUGHT_REQUIRED, result={"result" : False})

    if redis_support.exist_lock_twitter_search():
        # On Twitter search caused rate limit
        return api_bp.make_response(status=API_STATUS_RATE_LIMIT, result = {"result" : False, "ttl" : redis_support.ttl_exist_lock_twitter_search()})
    try:
        today = datetime.datetime.now().date()
        tss = TweetSearchSupport()
        ts = tss.get_ts()
        keen = Keen()

        character = charcollection.get_character(target_collection_number, target_character_number)
        if character == False:
            return api_bp.make_response(status=API_STATUS_UNCAUGHT_REQUIRED, result = {"result" : False})
        collection = charcollection.get_collection(target_collection_number)
        if collection == False:
            return api_bp.make_response(status=API_STATUS_UNCAUGHT_REQUIRED, result = {"result" : False})
        tso = tss.generate_tso([character.encode('UTF-8')], today)
        count_dict = dict()
        amount = 0
        for tweet in ts.search_tweets_iterable(tso):
            tweet_create_date = tss.to_datetime(tweet['created_at']).date()
            timestamp = tweet_create_date.strftime("%Y-%m-%dT03:00:00.000Z")
            if not count_dict.has_key(timestamp):
                count_dict[timestamp] = 1
            else:
                count_dict[timestamp] += 1

        seconds = (datetime.datetime.combine( datetime.datetime.now().date() 
                                            + datetime.timedelta(days=1), datetime.datetime.min.time()) - datetime.datetime.now()).seconds
        redis_support.refresh_expire_set(collection, target_character_number, seconds)
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


@api_bp.route('/test_twitter', methods=['GET'])
def test_event():
    try:
        tss = TweetSearchSupport()
        ts = tss.get_ts()
        today = datetime.datetime.now().date()
        tso = tss.generate_tso([u"アニメ".encode("UTF-8")],today, True)
        count = 0
        for tweet in ts.search_tweets_iterable(tso):
            tweet_text = ('%s @%s tweeted: %s' % (tweet['created_at'], tweet['user']['screen_name'], tweet['text']))
            print tweet_text
            count += 1
        return api_bp.make_response(status=API_STATUS_OK, result = {"result" : True , "count" : count})
    except TwitterSearchException as e:
        print e
        return api_bp.make_response(status=API_STATUS_UNKNOWN, result=dict())

@api_bp.route('/test_user_tweet', methods=['GET'])
def test_user_tweet():
    from twkorean import TwitterKoreanProcessor
    from util import PrintString
    ps = PrintString()

    try:
        tss = TweetSearchSupport()
        ts = tss.get_ts()
        today = datetime.datetime.now().date()
        tso = tss.generate_user_order("Twins", today)
        count = 0
        foreign_tweet_counter = 0
        hash_tags = set()
        processor = TwitterKoreanProcessor()
        for tweet in ts.search_tweets_iterable(tso):
            tweet_text = ('%s @%s tweeted: %s' % (tweet['created_at'], tweet['user']['screen_name'], tweet['text']))
            print tweet_text
            tokens = processor.tokenize(tweet['text'])
            new_tokens = []
            for token in tokens:
                foreign_flag = False
                if token.pos == 'Foreign':
                    if not foreign_flag:
                        foreign_tweet_counter += 1
                        foreign_flag = True
                elif token.pos == 'Hashtag':
                    hash_tags.add(token.text.encode('utf-8'))

                new_tokens.append((token.text.encode('utf-8'), token.pos))
            ps.print_tokens(new_tokens)
            count += 1
        print hash_tags
        return api_bp.make_response(status=API_STATUS_OK, result = {"result" : True , "count" : count, "foreign_count" : foreign_tweet_counter, "used_hashtags" : list(hash_tags)})
    except TwitterSearchException as e:
        print e
        return api_bp.make_response(status=API_STATUS_UNKNOWN, result=dict())
