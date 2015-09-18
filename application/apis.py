#!/usr/bin/env python
# -*- coding:utf8 -*-
import os
import datetime

from flask import Flask, request
from blueprint import APIBlueprint
from constants import API_STATUS_OK, API_STATUS_UNKNOWN

from TwitterSearch import TwitterSearchException

from keen_support import Keen
from tweet_support import TweetSearchSupport
import charcollection

api_bp = APIBlueprint('api', __name__, url_prefix='/api')
@api_bp.route('/get_twit', methods=['GET'])
def get_twit():
    target_character_number = request.args.get("character")
    target_collection_number = request.args.get("collection")
    if target_collection_number is None or target_character_number is None:
        return api_bp.make_response(status=API_STATUS_UNKNOWN, result = {"result" : False})
    try:
        today = datetime.datetime.now().date()
        tss = TweetSearchSupport()
        ts = tss.get_ts()
        keen = Keen()

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

        keen.add_girl(collection, character, count_dict)
        return api_bp.make_response(status=API_STATUS_OK, result={
            "result" : True
            })
    except TwitterSearchException as e:
        print e
        return api_bp.make_response(status=API_STATUS_UNKNOWN, result=dict())

@api_bp.route('/add_event', methods=['GET'])
def add_event():
    keen = Keen()
    return api_bp.make_response(status=API_STATUS_OK, result=dict(
            event_amount=keen.test_function()))
