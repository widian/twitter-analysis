#!/usr/bin/env python
# -*- coding:utf8 -*-
import os
import datetime

from flask import Flask
from blueprint import APIBlueprint
from constants import API_STATUS_OK, API_STATUS_UNKNOWN

from TwitterSearch import TwitterSearchException

from keen_support import Keen
from tweet_support import TweetSearchSupport

api_bp = APIBlueprint('api', __name__, url_prefix='/api')
@api_bp.route('/twit', methods=['GET'])
def get_twit():
    try:
        today = datetime.datetime.now().date()
        tss = TweetSearchSupport()
        ts = tss.get_ts()
        keen = Keen()
#        characters = ["시부야 린", "혼다 미오", "시마무라 우즈키", "후타바 안즈", "타카가키 카에데", "죠가사키 리카", "미무라 카나코", "칸자키 란코", "모로보시 키라리", "마에카와 미쿠", "타다 리아나", "죠가사키 미카", "코히나타 미호", "카와시마 미즈키", "토토키 아이리", "아베 나나", "닛타 미나미", "히노 아카네", "코시미즈 사치코", "시라사카 코우메", "아카기 미리아", "사쿠마 마유", "아나스타샤", "타카모리 아이코", "오가타 치에리", "카미야 나오", "호시 쇼코", "코바야카와 사에", "호죠 카렌", "호리 유코", "미야모토 프레데리카", "사가사와 후미카", "히메카와 유키", "이치노세 시키", "하야미 카나데", "이치하라 니나", "사쿠라이 모모카", "타치바나 아리스", "카타기리 사나에", "시오미 슈코", "아이바 유미", "무카이 타쿠미"]
        tso = tss.generate_tso("시부야 린", today)
        count_dict = dict()
        amount = 0
        for tweet in ts.search_tweets_iterable(tso):
            tweet_create_date = tss.to_datetime(tweet['created_at']).date()
            timestamp = tweet_create_date.strftime("%Y-%m-%dT03:00:00.000Z")
            if not count_dict.has_key(timestamp):
                count_dict[timestamp] = 1
            else:
                count_dict[timestamp] += 1
        keen.add_girl("cindemas", "시부야 린", count_dict)

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

