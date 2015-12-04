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
    
    target_id = 335204566

    result = sess.query(Relationship).filter(Relationship.following == target_id).all()
    for item in result:
        user = sess.query(User).filter(User.id  == item.follower).first()
        if user is None or user.tweet_collected_date is None or user.tweet_collected_date < datetime.datetime.now() - datetime.timedelta(days=14):
            result = timeline_crawler.crawling(user_id=item.follower)
            print result, item.follower
            while result is not True:
                if ErrorNumbers.RATE_LIMIT_ERROR in result:
                    print 'wait %d seconds' % (result[ErrorNumbers.RATE_LIMIT_ERROR] + 10)
                    time.sleep( result[ErrorNumbers.RATE_LIMIT_ERROR] + 10)
                    result = timeline_crawler.crawling(user_id=item.follower)
                else:
                    print "UNKNOWN ERROR "
                    break
        else:
            print 'pass ', user.screen_name
            continue

    #timeline_crawler.crawling(target_screen_name)
    #print timeline_crawler.get_rate_limit_status()
