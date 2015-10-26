#!/usr/bin/env python
# -*- coding:utf8 -*-

import time
from twitter import Api, TwitterError

from crawler import UserTimelineCrawler
from support.mysql_support import Session
from support.model import RateLimit, Relationship

if __name__ == '__main__':
    timeline_crawler = UserTimelineCrawler()
    GetSleepTime = Api().GetSleepTime
    sess = Session()

    result = sess.query(Relationship).filter(Relationship.following == target_id).all()
    for item in result:
        #TODO : crawling전에 crawling여부를 precheck 할수 있는 수단 만들어 두기
        #TODO : Rate Limit Handling (Rate Limit에 걸렸을 때 대기하기)
        timeline_crawler.crawling(user_id=item.follower)

    #timeline_crawler.crawling(target_screen_name)
    #print timeline_crawler.get_rate_limit_status()
