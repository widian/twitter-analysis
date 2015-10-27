#!/usr/bin/env python
# -*- coding:utf8 -*-

import time, datetime
from twitter import Api, TwitterError

from crawler import UserTimelineCrawler
from support.mysql_support import Session
from support.model import RateLimit, Relationship, User
from support.tweet_support import ErrorNumbers

if __name__ == '__main__':
    timeline_crawler = UserTimelineCrawler()
    GetSleepTime = Api().GetSleepTime
    sess = Session()
    
    target_id = 174193681

    result = sess.query(Relationship).filter(Relationship.following == target_id).all()
    for item in result:
        #TODO : Rate Limit Handling (Rate Limit에 걸렸을 때 대기하기)
        user = sess.query(User).filter(User.id  == item.follower).first()
        if user.tweet_collected_date is not None and user.tweet_collected_date > datetime.datetime.now() - datetime.timedelta(days=14):
            print 'pass ', user.screen_name
            continue
        else:
            print 'collect ', user.screen_name
            result = timeline_crawler.crawling(user_id=item.follower)
            while result is not True:
                if ErrorNumbers.RATE_LIMIT_ERROR in result:
                    print 'wait %d seconds' % (result[ErrorNumbers.RATE_LIMIT_ERROR] + 10)
                    time.sleep( result[ErrorNumbers.RATE_LIMIT_ERROR] + 10)
                    result = timeline_crawler.crawling(user_id=item.follower)
                else:
                    print " UNKNOWN ERROR "
                    break


    #timeline_crawler.crawling(target_screen_name)
    #print timeline_crawler.get_rate_limit_status()
