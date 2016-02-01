#!/usr/bin/env python
# -*- coding:utf8 -*-

""" path hack : http://stackoverflow.com/questions/6323860/sibling-package-imports
"""
import sys; import os
sys.path.insert(0, os.path.abspath('..'))

import time, datetime
from twitter import Api, TwitterError

from crawler import UserTimelineCrawler, UserLookupCrawler
from support.mysql_support import Session
from support.model import RateLimit, Relationship, User, UserDetail
from support.tweet_support import ErrorNumbers
from sqlalchemy import desc

def users_lookup_crawler():
    userdetail_crawler = UserLookupCrawler()

    sess = Session()

    subquery_collected_detail = sess.query(UserDetail.id).filter(UserDetail.updated_time > datetime.datetime.now() - datetime.timedelta(days=14)).subquery()
    query_result = sess.query(User.id).filter(~User.id.in_(subquery_collected_detail)).order_by(desc(User.id)).all()
    id_list = list()
    for item in query_result:
        id_list.append( item[0] )

    def get_result(userdetail_crawler, target_id_list):
        return userdetail_crawler.crawling(listof_user_id=target_id_list)

    while len(id_list) != 0:
        """ id_list를 받은 뒤, 맨 앞부터 100개씩 잘라냅니다.
        """
        target_id_list = id_list[:100]
        del(id_list[:100])

        result = get_result(userdetail_crawler, target_id_list)
        print "Lookup %s ~ %s" % (target_id_list[0], target_id_list[-1])
        while result is not True:
            if ErrorNumbers.RATE_LIMIT_ERROR in result:
                print 'wait %d seconds' % (result[ErrorNumbers.RATE_LIMIT_ERROR] + 10)
                try:
                    time.sleep( result[ErrorNumbers.RATE_LIMIT_ERROR] + 10)
                except Exception as e:
                    print result[ErrorNumbers.RATE_LIMIT_ERROR], e
                result = get_result(userdetail_crawler, target_id_list)
                print "Lookup %s ~ %s" % (target_id_list[0], target_id_list[-1])
            else:
                #TODO : 대개 요청을 했는데, 정보가 안넘어오면 이 위치에서 어떤 에러가 발생하는듯
                print "UNKNOWN ERROR "
                break
    sess.close()

if __name__ == '__main__':
    users_lookup_crawler()
