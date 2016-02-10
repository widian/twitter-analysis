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
from sqlalchemy import asc, or_

def timeline_crawler():
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
    
    #TODO : 각각의 horizontal partition에 대해 get_result부분이 변할 수 있도록 해야함. since_id 혹은 since를 외부 테이블 정보로부터 받아올 수 있도록
    since_id = 680056873668620289
    subquery_collected_date = sess.query(User.id).filter(or_(
        User.tweet_collected_date == None, 
        User.tweet_collected_date < datetime.datetime.now() - datetime.timedelta(days=14)))\
                .subquery()
    result = sess.query(Relationship).filter(Relationship.follower.in_(subquery_collected_date))\
                                     .filter(Relationship.following == target_id).all()

    userdetail_crawler = UserLookupCrawler()
    def usermodellist_to_idlist(relationship_list):
        result = list()
        for item in relationship_list:
            result.append(item.follower)
        return result

    def is_target(since_id, relationship, lookup_result):
        """ LookupCache에 없는 유저는 무조건 수집
            Cache에는 있지만, 가장 최근 트윗이 since_id보다 작거나, None인 유저는 수집하지 않음.
            crawling_list에 relationship을 추가하는 걸로 수집결정
        """     
        if not isinstance(lookup_result, list):
            #NOTE : 이 부분을 내가 왜넣었을까.
            return True

        for item in lookup_result:
            if relationship.follower == item.id:
                if item.latest_status_id is None or item.latest_status_id < since_id:
                    return False
                else:
                    return True
        return True

    while len(result) != 0:
        crawling_list = list()
        lookup_list = result[:100]
        id_list = usermodellist_to_idlist(lookup_list)
        lookup_cache = sess.query(UserDetail).filter(UserDetail.id.in_(id_list)).order_by(asc(UserDetail.id)).all()

        lookup_result = userdetail_crawler.get(listof_user_id=id_list)
        while not isinstance(lookup_result, list):
            if ErrorNumbers.RATE_LIMIT_ERROR in lookup_result:
                print 'wait %d seconds' % (lookup_result[ErrorNumbers.RATE_LIMIT_ERROR] + 10)
                try:
                    time.sleep( lookup_result[ErrorNumbers.RATE_LIMIT_ERROR] + 10)
                except IOError as e:
                    print lookup_result
                except Exception as e:
                    print lookup_result[ErrorNumbers.RATE_LIMIT_ERROR], e
                lookup_result = userdetail_crawler.get(listof_user_id=id_list)
            else:
                print "UNKNOWN ERROR ", lookup_result
                break
        for item in lookup_list:
            if is_target(since_id, item, lookup_result):
                crawling_list.append(item)
        del(result[:100])
        automatic_crawling(since_id, crawling_list)
    sess.close()

def automatic_crawling(since_id, crawling_list):
    timeline_crawler = UserTimelineCrawler()
    sess = Session()
    def get_result(timeline_crawler, follower):
        return timeline_crawler.crawling(user_id=follower, since_id=since_id)
    #    return timeline_crawler.crawling(user_id=follower, since=datetime.datetime(year=2015, month=12, day=7, hour=1, minute=28, second=36))

    for item in crawling_list:
        #TODO : user체크를 이제 상위 함수에서 처리하고 있기 때문에, 이쪽 루틴을 철거해야함
        result = get_result(timeline_crawler, item.follower)
        print result, item.follower
        while result is not True:
            if ErrorNumbers.RATE_LIMIT_ERROR in result:
                print 'wait %d seconds' % (result[ErrorNumbers.RATE_LIMIT_ERROR] + 10)
                try:
                    time.sleep( result[ErrorNumbers.RATE_LIMIT_ERROR] + 10)
                except IOError as e:
                    print result
                except Exception as e:
                    print result[ErrorNumbers.RATE_LIMIT_ERROR], e
                result = get_result(timeline_crawler, item.follower)
            #TODO : Suspended error handling을 추가해야함
            else:
                print "UNKNOWN ERROR "
                break
    sess.close()
    return True

if __name__ == '__main__':
    timeline_crawler()
