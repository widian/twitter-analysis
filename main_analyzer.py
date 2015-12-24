#!/usr/bin/env python
# -*- coding:utf8 -*-
import datetime, time
import analyzer
from support.model import Tweet_335204566, Tweet_281916923

analysis_type = analyzer.AnalysisType( since=datetime.datetime(2015, 11, 1, 0, 0, 0), 
                  until=datetime.datetime(2015, 12, 1, 0, 0, 0), 
                  follower_of=335204566,
                  contain_retweet=0,
                  contain_english=0,
                  contain_username_mentioned=2,
                  contain_linked_tweet=0,
                  least_tweet_per_user=200)
start = time.time()

""" Follower tweets table made order ->
"""
tweet_list = Tweet_335204566 + Tweet_281916923
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
