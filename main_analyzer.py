#!/usr/bin/env python
# -*- coding:utf8 -*-
import datetime, time
import analyzer
from support.model import Tweet_335204566, Tweet_281916923, Tweet_44771983
from support.mysql_support import Session, AnalysisSession
""" AnalysisType Explanation

    contained_linked_tweet : 0 - 링크가 포함된 트윗을 제외, 1 - 링크가 포함된 트윗을 검색, 2 - 링크가 포함된 트윗만 검색
    contain_english : 0 - 외국어권 유저로 추정되는 유저의 트윗을 제외, 1 - 외국어권 유저의 트윗을 검색, 2 - 외국어권 유저의 트윗만 검색
    contain_username_mentioned : 0 - 특정 유저에게 답변한 트윗을 제외, 1 - 특정 유저에게 답변한 트윗을 포함, 2 - 특정 유저에게 답변한 트윗만 검색
    contain_retweet : 0 - 리트윗을 제외, 1 - 리트윗한 트윗을 검색, 2 - 리트윗한 트윗만 검색
    least_tweet_per_user : 특정 유저가 least_tweet_per_user만큼의 트윗을 하지 않았다면 검색하지 않음.

    follower_of : follower_of의 follower인 트윗만 검색
    since : since부터의 트윗만 검색
    until : until까지의 트윗만 검색
"""
tweet_list = Tweet_335204566 + Tweet_281916923 + Tweet_44771983

def recollect(type_number):
    analysis_type = analyzer.produce_analysis_type(type_number)
    print "type_number :", type_number, analysis_type
    result = analyzer.tweet_reduce(analysis_type, tweet_list)

def analysis(analysis_type):
    start = time.time()

    """ Follower tweets table made order ->
    """
    result = analyzer.tweet_reduce( analysis_type , tweet_list)
    print time.time() - start, " for get tweet list"
    start = time.time()
    print "number of words : %d" % analyzer.analysis_tweets(analysis_type, result)
    print time.time() - start, " for analysis tweet list"
    start = time.time()
    print "number of tweets : %d" % len(result)
    sess = Session()
    analyzer.export_result_to_csv(analysis_type.get_type_id(sess))
    print time.time() - start, " for export result to csv file"
    sess.close()
    print "END"
    return True

if __name__=='__main__':
    recollect(10)
    recollect(11)
    recollect(13)
    recollect(14)
    recollect(15)
    recollect(16)
    recollect(17)

#    analysis_type = analyzer.AnalysisType( since=datetime.datetime(2015, 11, 1, 0, 0, 0), 
#                      until=datetime.datetime(2015, 12, 1, 0, 0, 0), 
#                      follower_of=335204566,
#                      contain_retweet=0,
#                      contain_english=0,
#                      contain_username_mentioned=0,
#                      contain_linked_tweet=2,
#                      least_tweet_per_user=200)
#    analysis(analysis_type)
