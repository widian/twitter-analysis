#!/usr/bin/env python
# -*- coding:utf8 -*-

import datetime

from TwitterSearch import TwitterSearchException
from twitter import TwitterError 
from sqlalchemy import create_engine

from support.tweet_support import TweetSupport
try:
    from config import SQLALCHEMY_DATABASE_URI
except:
    print 'SQLALCHEMY_DATABASE_URI is not exist'
    exit()

engine = create_engine(SQLALCHEMY_DATABASE_URI)


def crawling_tweet_user():
    try:
        ts = TweetSupport()
        api = ts.get_api()
        try:
            minimal_max_id = None
            while True:
                statuses = api.GetSearch(
                        term=u"미오",
                        count=3000,
                        max_id=minimal_max_id,
                        include_entities=True)
                minimal_max_id = None
                for tweet in statuses:
                    tweet_text = ('%s %s @%s tweeted: %s' % (tweet.id, tweet.created_at, tweet.GetUser().screen_name, tweet.text))
                    minimal_max_id = tweet.id
                    print tweet_text 
                if minimal_max_id is None:
                    break
                else:
                    minimal_max_id -= 1
        except TwitterError as f:
            print f
            return True
    except TwitterError as e:
        print e

def get_followers():
    try:
        ts = TweetSupport()
        api = ts.get_api()
        follower_ids = api.GetFollowerIDs(screen_name='saenuridang')
        print len(follower_ids)
#        for follower in follower_ids:
#            try:
#                print "------------%s-----------" % (follower)
#                print api.GetUser(user_id=follower).GetDescription()
#            except TwitterError as api_error:
#                print api_error
    except TwitterError as e:
        print e

def get_rate_limit_status():
    try:
        ts = TweetSupport()
        api = ts.get_api()
        print api.GetRateLimitStatus()
    except TwitterError as e:
        print e

def get_user_info(screen_name):
    try:
        ts = TweetSupport()
        api = ts.get_api()
        print api.GetUser(screen_name=screen_name)
    except TwitterError as e:
        print e
if __name__ == "__main__":
#    crawling_tweet_user()
#    get_followers()
#    get_rate_limit_status()
#    get_user_info('lys2419')
    print 'do nothing'
