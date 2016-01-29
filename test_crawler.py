#!/usr/bin/env python
# -*- coding:utf8 -*-

import crawler
from twitter import TwitterError 

from support.tweet_support import TweetSupport, TweetErrorHandler, ErrorNumbers

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
def korean_test():
    print u"Start checking Korean Character Validate"
    start = u"\uac00"
    end = u"\ud7a3"
    c = UserTimelineCrawler()
    for i in xrange(ord(start), ord(end) + 1):
        if c.parse_ignore(unichr(i)) == unichr(i):
            print unichr(i), c.parse_ignore(unichr(i))
            continue
        else:
            print "error!"
            return False
    print u"Start Checking smaller and equal than \U0000FFFF"
    start = u"\U00000000"
    end = u"\U0000FFFF"
    for i in xrange(ord(start), ord(end) + 1):
        if c.parse_ignore(unichr(i)) == unichr(i):
            continue
        elif i == 8230 or i == 9410 or (i >= 9728 and i<= 10175):
            continue
        else:
            print unichr(i), i
            print "error!"
            return False
    print "Finished"
    return True
def timeline_crawling_too_long_tweet_handler():
    sess = Session()
    a = ''
    for i in xrange(1, 150):
        a += 'b'

    tweet = Tweet(
            123,
            a, 
            123,
            datetime.datetime.now() - datetime.timedelta(days=5))
    tweet2 = Tweet(
            455,
            a,
            455,
            datetime.datetime.now() - datetime.timedelta(days=5))
    tweet3 = Tweet(
            456,
            'asdf',
            456,
            datetime.datetime.now() - datetime.timedelta(days=5))
    sess.add(tweet)
#    sess.add(tweet2)
    sess.add(tweet3) # tweet3 need to add correctly
    try:
        sess.commit()
    except DataError, exc:
        sess.rollback()
        #TODO: statement를 활용해서 Reflection으로 rewrap하기 
        #print exc.statement

        #NOTE : error tweet for two or more error twits
        # INSERT INTO tweet (id, text, user, retweet_owner, retweet_origin, created_at, collected_date, reply_to) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        # ((123, 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 123, None, None, datetime.datetime(2015, 11, 17, 4, 35, 12, 177278), datetime.datetime(2015, 11, 22, 4, 35, 12, 163143), None), (455, 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 455, None, None, datetime.datetime(2015, 11, 17, 4, 35, 12, 181056), datetime.datetime(2015, 11, 22, 4, 35, 12, 163143), None)) 
        if isinstance(exc.params[0], tuple):
            #TODO : error tweet이 2개 이상
            count = 0
            for item in exc.params:
                print len(item[1])
                if len(item[1]) > 140:
                    error_tweet = ErrorTweet(
                            item[0],
                            item[1],
                            item[2],
                            item[5])
                    sess.add(error_tweet)
                else:
                    tweet = Tweet(
                            item[0],
                            item[1],
                            item[2],
                            item[5])
                    sess.add(tweet)
                count += 1
            sess.commit()
            print "length : ", count
        else:
            #TODO : error tweet이 1개
            error_tweet = ErrorTweet(
                    exc.params[0],
                    exc.params[1],
                    exc.params[2],
                    exc.params[5])
            sess.add(error_tweet)
            sess.commit()
        print dir(exc), exc.message, exc.statement, exc.params, len(exc.params), isinstance(exc.params[0], tuple)

    sess.close()
#    timeline_crawling_too_long_tweet_handler()
#    korean_test()
#    crawling_tweet_search()
#    print UserTimelineCrawler().get_rate_limit_status()
#    UserFollowerIDs().crawling('twit_reva')
#    UserTimelineCrawler().crawling('deresute_border')

def make_table_create_query():
    """ http://stackoverflow.com/questions/2128717/sqlalchemy-printing-raw-sql-from-create
    """ 
    from support.model import UserDetail
    from sqlalchemy.schema import CreateTable
    from support.mysql_support import engine
    print CreateTable(UserDetail.__table__).compile(engine)

make_table_create_query()
