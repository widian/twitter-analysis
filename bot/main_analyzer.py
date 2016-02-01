#!/usr/bin/env python
# -*- coding:utf8 -*-
""" path hack : http://stackoverflow.com/questions/6323860/sibling-package-imports
"""
import sys; import os
sys.path.insert(0, os.path.abspath('..'))

import datetime, time
import analyzer
from support.model import Tweet_335204566, Tweet_281916923, Tweet_44771983, Tweet_155884548
from support.mysql_support import Session, AnalysisSession
""" AnalysisType Explanation

    contained_linked_tweet : 0 - 링크가 포함된 트윗을 제외, 1 - 링크가 포함된 트윗을 검색, 2 - 링크가 포함된 트윗만 검색
    contain_english : 0 - 외국어권 유저로 추정되는 유저의 트윗을 제외, 1 - 외국어권 유저의 트윗을 검색, 2 - 외국어권 유저의 트윗만 검색
    contain_username_mentioned : 0 - 특정 유저에게 답변한 트윗을 제외, 1 - 특정 유저에게 답변한 트윗을 포함, 2 - 특정 유저에게 답변한 트윗만 검색
    contain_retweet : 0 - 리트윗을 제외, 1 - 리트윗한 트윗을 검색, 2 - 리트윗한 트윗만 검색
    least_tweet_per_user : 특정 유저가 least_tweet_per_user만큼의 트윗을 하지 않았다면 검색하지 않음.
    user_list_type : 0 - 모든 유저를 검색, not 0 - UserList를 확인해서 user_list_type와 같은 list_type값을 가진 user_id의 리스트에 속하는 유저들의 트윗을 검색

    follower_of : follower_of의 follower인 트윗만 검색
    since : since부터의 트윗만 검색
    until : until까지의 트윗만 검색

"""
tweet_list = Tweet_335204566 + Tweet_281916923 + Tweet_44771983 + Tweet_155884548

def recollect(type_number):
    analysis_type = analyzer.produce_analysis_type(type_number)
    print "type_number :", type_number, analysis_type
    result = analyzer.tweet_reduce(analysis_type, tweet_list)

def analysis(analysis_type):
    start = time.time()

    """ Follower tweets table made order ->
    """
    result = analyzer.tweet_reduce( analysis_type , tweet_list)
    print "number of tweets : %d" % len(result)
    print time.time() - start, " for get tweet list"
    start = time.time()

    print "number of words : %d" % analyzer.analysis_tweets(analysis_type, result)
    print time.time() - start, " for analysis tweet list"
    start = time.time()

    sess = Session()
    analyzer.export_result_to_csv(analysis_type.get_type_id(sess))
    print time.time() - start, " for export result to csv file"
    sess.close()
    print "END"
    return True

def make_user_list(user_list):
    if not isinstance(user_list, list):
        return None
    sess = Session()
    user_list_type = UserListType()
    return user_list_type.add_user_list(sess, user_list)

    sess.close()
if __name__=='__main__':
#    analysis(analyzer.produce_analysis_type(18))

    analysis_type = analyzer.AnalysisType( since=datetime.datetime(2015, 11, 1, 0, 0, 0), 
                      until=datetime.datetime(2015, 12, 1, 0, 0, 0), 
                      follower_of=155884548,
                      contain_retweet=0,
                      contain_english=0,
                      contain_username_mentioned=0,
                      contain_linked_tweet=0,
                      least_tweet_per_user=200)
    analysis(analysis_type)
