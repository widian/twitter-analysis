#!/usr/bin/env python
# -*- coding:utf8 -*-

import datetime

from TwitterSearch import TwitterSearchException
from twitter import TwitterError 

from application.tweet_support import TweetSearchSupport
from application.tweet_support import TweetSupport

def crawling_tweet_user():
    from twkorean import TwitterKoreanProcessor
    from application.util import PrintString
    ps = PrintString()
    try:
        tss = TweetSearchSupport()
        ts = tss.get_ts()
        today = datetime.datetime.now().date()
        tso = tss.generate_user_order("lys2419", today)
        count = 0
        foreign_tweet_counter = 0
        hash_tags = set()
        processor = TwitterKoreanProcessor()
        for tweet in ts.search_tweets_iterable(tso):
            tweet_text = ('%s %s @%s tweeted: %s' % (tweet['id'], tweet['created_at'], tweet['user']['screen_name'], tweet['text']))
            print tweet_text, tweet
            tokens = processor.tokenize(tweet['text'])
            for token in tokens:
                # Tokenize된 Token들에서 정보 추출하는 부분.
                foreign_flag = False
                if token.pos == 'Foreign':
                    if not foreign_flag:
                        foreign_tweet_counter += 1
                        foreign_flag = True
                elif token.pos == 'Hashtag':
                    hash_tags.add(token.text.encode('utf-8'))
            ps.print_tokens(tokens)
            count += 1
            break
        return True
    except TwitterSearchException as e:
        print e
        return True

def get_followers():
    try:
        ts = TweetSupport()
        api = ts.get_api()
        follower_ids = api.GetFollowerIDs(screen_name='ancom21c')
        for follower in follower_ids:
            try:
                print "------------%s-----------" % (follower)
                print api.GetUser(user_id=follower).GetDescription()
            except TwitterError as api_error:
                print api_error
    except TwitterError as e:
        print e

def get_rate_limit_status():
    try:
        ts = TweetSupport()
        api = ts.get_api()
        print api.GetRateLimitStatus()
    except TwitterError as e:
        print e
if __name__ == "__main__":
#    crawling_tweet_user()
#    get_followers()
    get_rate_limit_status()
