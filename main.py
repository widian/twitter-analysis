#!/usr/bin/env python
# -*- coding:utf8 -*-

import time, datetime
from twitter import Api, TwitterError

from crawler import UserTimelineCrawler, UserLookupCrawler
from support.mysql_support import Session
from support.model import RateLimit, Relationship, User, UserDetail
from support.tweet_support import ErrorNumbers

def timeline_crawler():
    timeline_crawler = UserTimelineCrawler()
    sess = Session()
    
    """ NC 다이노스 """
    #target_id = 335204566

    """ 삼성 라이온즈 """
    #target_id = 281916923

    """ 기아 타이거즈 """
    target_id = 44771983

    """ 레바 """
    #target_id = 155884548
    """ """
    
    def get_result(timeline_crawler, follower):
        return timeline_crawler.crawling(user_id=follower, since_id=680056873668620289)
    #    return timeline_crawler.crawling(user_id=follower, since=datetime.datetime(year=2015, month=12, day=7, hour=1, minute=28, second=36))


    result = sess.query(Relationship).filter(Relationship.following == target_id).all()
    for item in result:
        user = sess.query(User).filter(User.id  == item.follower).first()
        if user is None or user.tweet_collected_date is None or user.tweet_collected_date < datetime.datetime.now() - datetime.timedelta(days=14):
            result = get_result(timeline_crawler, item.follower)
            print result, item.follower
            while result is not True:
                if ErrorNumbers.RATE_LIMIT_ERROR in result:
                    print 'wait %d seconds' % (result[ErrorNumbers.RATE_LIMIT_ERROR] + 10)
                    try:
                        time.sleep( result[ErrorNumbers.RATE_LIMIT_ERROR] + 10)
                    except Exception as e:
                        print result[ErrorNumbers.RATE_LIMIT_ERROR], e
                    result = get_result(timeline_crawler, item.follower)
                    if user is None or user.screen_name is None:
                        pass
                    else:
                        print 'pass ', user.screen_name
                else:
                    print "UNKNOWN ERROR "
                    break
        else:
            print 'pass ', user.screen_name
            continue

if __name__ == '__main__':
    timeline_crawler()
