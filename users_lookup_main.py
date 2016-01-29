#!/usr/bin/env python
# -*- coding:utf8 -*-

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

    #TODO : target_id_list를 100개 씩 잘라서 넣기.
    def get_result(userdetail_crawler, target_id_list):
        return userdetail_crawler.crawling(listof_user_id=target_id_list)

    while len(id_list) != 0:
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
                print "UNKNOWN ERROR "
                break
    sess.close()

if __name__ == '__main__':
    users_lookup_crawler()
