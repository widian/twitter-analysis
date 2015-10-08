#!/usr/bin/env python
# -*- coding:utf8 -*-

import datetime, re
from email.utils import parsedate_tz
from HTMLParser import HTMLParser

from TwitterSearch import TwitterSearchException
from twitter import TwitterError 

from support.tweet_support import TweetSupport, TweetErrorHandler
from support.mysql_support import Session
from support.model import RateLimit, User, Tweet

from sqlalchemy import func

class Crawler(object):
    ts = None
    api = None
    hparser = None
    def __init__(self):
        self.ts = TweetSupport()
        self.api = self.ts.get_api()
        self.hparser = HTMLParser()

    def parse_ignore(self, text):
        """ referenced from
            http://stackoverflow.com/questions/26568722/remove-unicode-emoji-using-re-in-python
        """
        myre = None
        try:
            # Wide UCS-4 build
            myre = re.compile(u'['
                    u'\U0001F300-\U0001F64F'
                    u'\U0001F680-\U0001F6FF'
                    u'\u2600-\u26FF\u2700-\u27BF]+', 
                    re.UNICODE)
        except re.error:
            # Narrow UCS-2 build
            myre = re.compile(u'('
                    u'\ud83c[\udf00-\udfff]|'
                    u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
                    u'[\u2600-\u26FF\u2700-\u27BF])+', 
                    re.UNICODE)
        text = self.hparser.unescape(text)
        return myre.sub('', text)

    def get_rate_limit_status(self):
        try:
            print self.api.GetRateLimitStatus()
        except TwitterError as e:
            # NOTE NOTE NOTE NOTE
            # 아마도 RateLimitStatus까지 RateLimit에 걸린 상황에 해당 루틴으로 들어올 가능성 높음
            # 해당 경우에는 모든 프로세스를 종료하고 로그를 남기는방향이
            print e

    def rate_limit_handler(self, case, 
            process_name=None, 
            minimal_max_id=None, 
            limit_since=None):
        sess = Session()
        sess.add(RateLimit(limit_since, process_name, minimal_max_id=minimal_max_id))
        sess.commit()
        sess.close()
        print 'rate limit!'
        print case['message']
    def to_datetime(self, datestring):
        """ referenced from
            http://stackoverflow.com/questions/7703865/going-from-twitter-date-to-python-datetime-date
        """
        time_tuple = parsedate_tz(datestring.strip())
        dt = datetime.datetime(*time_tuple[:6])
        return dt - datetime.timedelta(seconds=time_tuple[-1])
   
class UserTimelineCrawler(Crawler):
    minimal_max_id = None
    def __init__(self):
        Crawler.__init__(self)
    
    def crawling(self, username):
        sess = None
        try:
            sess = Session()
            cached_max_id_row = sess.query(func.min(Tweet.id)).first()
            if cached_max_id_row[0] is not None:
                self.minimal_max_id = cached_max_id_row[0] - 1
            while True:
                statuses = self.api.GetUserTimeline(
                        screen_name=username,
                        max_id=self.minimal_max_id)
                self.minimal_max_id = None
                for tweet in statuses:
                    tweet_text = ('%s %s @%s tweeted: %s' % (tweet.id, tweet.created_at, tweet.GetUser().screen_name, tweet.text))
                    self.minimal_max_id = tweet.id
                    exist = sess.query(Tweet).filter(Tweet.id==tweet.id).first()
                    if not exist:
                        sess.add(Tweet(
                            tweet.id,
                            self.parse_ignore(tweet.text),
                            tweet.GetUser().id,
                            self.to_datetime(tweet.created_at)))
                    sess.commit()
                    sess.close()
                    print tweet_text 

                if self.minimal_max_id is None:
                    break
                else:
                    self.minimal_max_id -= 1
            sess.commit()
            sess.close()
            return True
        except TwitterError as e:
            t = TweetErrorHandler(e)
            t.add_handler(88, self.rate_limit_handler)
            t.invoke(process_name='user_tweet', minimal_max_id=8, limit_since=datetime.datetime.now())
            if sess is not None:
                sess.commit()
                sess.close()
            return False

if __name__ == "__main__":
    def crawling_tweet_search():
        try:
            ts = TweetSupport()
            api = ts.get_api()
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
            return True
        except TwitterError as e:
            print e
            return True

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
#    crawling_tweet_search()
#    get_followers()
#    get_rate_limit_status()
#    get_user_info('lys2419')
    UserTimelineCrawler().crawling('twittlions')
