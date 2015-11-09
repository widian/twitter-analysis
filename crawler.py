#!/usr/bin/env python
# -*- coding:utf8 -*-

import datetime, re
from email.utils import parsedate_tz
from HTMLParser import HTMLParser

from twitter import TwitterError 

from support.tweet_support import TweetSupport, TweetErrorHandler, ErrorNumbers
from support.mysql_support import Session
from support.model import RateLimit, User, Tweet, Relationship

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

class Crawler(object):
    ts = None
    api = None
    hparser = None
    process_name = None
    def __init__(self):
        self.ts = TweetSupport()
        self.api = self.ts.get_api()
        self.hparser = HTMLParser()

    def crawling(self, user_id):
        #TODO : NEED TO RAISE NOT IMPLEMENTED ERROR
        print "NOT IMPLEMENTED CRAWLING FUNCTION"
        return False
    
    def parse_ignore(self, text):
        """ referenced from
            http://stackoverflow.com/questions/26568722/remove-unicode-emoji-using-re-in-python
        """
        myre = None
        try:
            # Wide UCS-4 build
#            \U0001f1f0\U0001f1f7
            #TODO : 그냥 모든 unrecognized unicode string을 제거하도록 수정해야할듯.
            myre = re.compile(u'['
                    u'\U0001F1E6-\U000FFFFF'
                    u'\u2600-\u26FF\u2700-\u27BF]+', 
                    re.UNICODE)
        except re.error:
            # Narrow UCS-2 build
            myre = re.compile(u'('
                    u'\ud83c[\udde6-\udfff]|'
                    u'\ud83d[\ud000-\udeff]|'
                    u'[\ud84d\uc000-\uffff\uffff]|'
                    u'[\u2600-\u26FF\u2700-\u27BF])+', 
                    re.UNICODE)
        text = self.hparser.unescape(text)
        return myre.sub('', text)

    def get_rate_limit_status(self):
        try:
            return self.api.GetRateLimitStatus()
        except TwitterError as e:
            # NOTE NOTE NOTE NOTE
            # 아마도 RateLimitStatus까지 RateLimit에 걸린 상황에 해당 루틴으로 들어올 가능성 높음
            # 해당 경우에는 모든 프로세스를 종료하고 로그를 남기는방향이
            print e

    def rate_limit_handler(self, case, 
            process_name=None, 
            minimum_max_id=None):
        sess = Session()
        cached_rate_limit = sess.query(RateLimit) \
                                .filter(RateLimit.process_name == process_name) \
                                .filter(RateLimit.limit > datetime.datetime.now()).first()
        wait_until = None
        if cached_rate_limit is not None:
            #TODO : process wait until rate limit is broken
            print "wait to", cached_rate_limit.limit
            wait_until = cached_rate_limit.limit
        else:
            rate_limit = self.get_rate_limit_status()
            items = process_name.split('/')
            target_dict = rate_limit['resources'][items[1]][process_name]
            limit_since = datetime.datetime.fromtimestamp(int(target_dict['reset']))
            sess.add(RateLimit(limit_since, process_name, minimum_max_id=minimum_max_id))
            sess.commit()
            print "wait to", limit_since
            wait_until = limit_since
        sess.close()
        #TODO : wait process and restart from rate_limit row information
        print 'rate limit!'
        return (wait_until - datetime.datetime.now() ).total_seconds()

    def to_datetime(self, datestring):
        """ referenced from
            http://stackoverflow.com/questions/7703865/going-from-twitter-date-to-python-datetime-date
        """
        time_tuple = parsedate_tz(datestring.strip())
        dt = datetime.datetime(*time_tuple[:6])
        return dt - datetime.timedelta(seconds=time_tuple[-1])

    def user_info( func ):
        """ 특정 crawling이 어떤 user대상이라면, 미리 user정보를 받아오기 위한
            decorator함수. 
        """
        def get_user_info(self, screen_name=None, user_id=None):
            process_name = "/users/show/: id"
            sess = Session()
            """ 만약 해당 유저정보가 이미 저장되어있다면
            """
            exist = sess.query(User).filter(or_(User.screen_name == screen_name,
                                                User.id == user_id)).first()
            if exist:
                """ 세션을 닫고 해당 유저의 id를 추가로 전달. screen_name을 받든, user_id를 받든
                    crawling 함수에는 user_id를 전달함
                """
                sess.close()
                return func(self, exist.id)
            else:
                try:
                    """ Twitter로부터 유저정보를 받은 뒤 DB에 저장.
                    """
                    ts = TweetSupport()
                    api = ts.get_api()
                    user = api.GetUser(screen_name=screen_name, user_id=user_id)
                    user_chunk = User(
                        user.id,
                        user.name,
                        user.screen_name,
                        user.statuses_count,
                        user.followers_count)
                    sess.add(user_chunk)
                    sess.commit()
                    sess.close()
                    return func(self, user.id)
                except TwitterError as e:
                    """ Error처리는 다른 함수와 동일
                    """
                    t = TweetErrorHandler(e)
                    t.add_handler(ErrorNumbers.RATE_LIMIT_ERROR, self.rate_limit_handler)
                    result = t.invoke(process_name=process_name)
                    if sess is not None:
                        sess.commit()
                        sess.close()
                    return result 
        return get_user_info
    user_info = staticmethod(user_info)
   
class UserTimelineCrawler(Crawler):
    minimum_max_id = None
    def __init__(self):
        Crawler.__init__(self)
        self.process_name = '/statuses/user_timeline'
    
    @Crawler.user_info
    def crawling(self, user_id):
        # sess => session
        sess = None
        try:
            sess = Session()
            cached_maximum_id = None
            while True:
                # This routine must be shutdowned when result doesn't exist.
                statuses = self.api.GetUserTimeline(
                        user_id=user_id,
                        count=200,
                        max_id=self.minimum_max_id)
                self.minimum_max_id = None

                for tweet in statuses:
                    if cached_maximum_id is None:
                        cached_row = sess.query(func.max(Tweet.id)).filter(Tweet.user == user_id).first()
                        if cached_row[0] is None:
                            cached_maximum_id = 0
                        else:
                            """ cache에서 가지고 있는 minimum id를 새 minimum_max_id로 지정해줌. 
                            """
                            cached_maximum_id = cached_row[0]
                    self.minimum_max_id = tweet.id
                    exist = sess.query(Tweet).filter(Tweet.id==tweet.id).first()
                    if not exist:
                        # Make Data Row for add to table
                        tweet_chunk = Tweet(
                            tweet.id,
                            self.parse_ignore(tweet.text),
                            tweet.user.id,
                            self.to_datetime(tweet.created_at))
                        if tweet.retweeted_status:
                            tweet_chunk.retweet_owner = tweet.retweeted_status.user.id
                            tweet_chunk.retweet_origin = tweet.retweeted_status.id
                        if tweet.in_reply_to_user_id:
                            tweet_chunk.reply_to = tweet.in_reply_to_user_id
                        sess.add(tweet_chunk)

                    """ print tweet search result (Unnecessary)
                    """
                    tweet_text = ('%s %s @%s tweeted: %s' % (tweet.id, tweet.created_at, tweet.GetUser().screen_name, tweet.text))
                    print tweet_text 
                if self.minimum_max_id is None:
                    """ No result with self.api.GetUSerTimeline
                    """
                    break
                else:
                    """ 만약 캐시된 tweet_id의 maximum이 이번 검색에서 얻은 minimum_id보다 작다면
                    """
                    if cached_maximum_id > self.minimum_max_id:
                        cached_row = sess.query(func.min(Tweet.id)).filter(Tweet.user == user_id).first()
                        self.minimum_max_id = cached_row[0]
                    """ 최종에는 - 1
                    """
                    self.minimum_max_id -= 1
            sess.commit()
            target_user = sess.query(User).filter(User.id == user_id).first()
            target_user.tweet_collected_date = datetime.datetime.now()
            sess.commit()
            sess.close()
            return True
        except TwitterError as e:
            t = TweetErrorHandler(e)
            t.add_handler(ErrorNumbers.RATE_LIMIT_ERROR, self.rate_limit_handler)
            result = t.invoke(process_name=self.process_name, minimum_max_id=self.minimum_max_id)
            if sess is not None:
                sess.commit()
                sess.close()
            return result 

class UserFollowerIDs(Crawler):
    def __init__(self):
        Crawler.__init__(self)
        self.process_name = '/followers/ids'

    @Crawler.user_info
    def crawling(self, user_id):
        sess = None
        try:
            ts = TweetSupport()
            api = ts.get_api()
            follower_ids = api.GetFollowerIDs(user_id=user_id)
            sess = Session()
            remained = len(follower_ids)
            for id in follower_ids:
                remained -= 1
                print "add ", remained
                exist = sess.query(Relationship).filter(Relationship.following == user_id).filter(Relationship.follower == id).first()
                if exist:
                    continue
                else:
                    relationship_chunk = Relationship(
                            user_id,
                            id)
                    sess.add(relationship_chunk)
            sess.commit()
            sess.close()
            return True
        except TwitterError as e:
            t = TweetErrorHandler(e)
            t.add_handler(ErrorNumbers.RATE_LIMIT_ERROR, self.rate_limit_handler)
            result = t.invoke(process_name=self.process_name)
            if sess is not None:
                sess.commit()
                sess.close()
            return result 

if __name__ == "__main__":
    def crawling_tweet_search():
        try:
            ts = TweetSupport()
            api = ts.get_api()
            minimum_max_id = None
            while True:
                statuses = api.GetSearch(
                        term=u"미오",
                        count=3000,
                        max_id=minimum_max_id,
                        include_entities=True)
                minimum_max_id = None
                for tweet in statuses:
                    tweet_text = ('%s %s @%s tweeted: %s' % (tweet.id, tweet.created_at, tweet.GetUser().screen_name, tweet.text))
                    minimum_max_id = tweet.id
                    print tweet_text 
                if minimum_max_id is None:
                    break
                else:
                    minimum_max_id -= 1
            return True
        except TwitterError as e:
            print e
            return True

#    crawling_tweet_search()
    print UserTimelineCrawler().get_rate_limit_status()
#`    UserFollowerIDs().crawling('Kiatigers')
