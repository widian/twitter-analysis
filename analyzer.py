#!/usr/bin/env python
# -*- coding:utf8 -*-

from support.mysql_support import Session
from support.model import Tweet
from collections import OrderedDict

from twkorean import TwitterKoreanProcessor

def analyze():
    sess = Session()
    processor = TwitterKoreanProcessor(stemming=False)
    tweets = sess.query(Tweet)\
                 .filter(Tweet.user == 222400625) \
                 .all()
    noun_usage_dict = OrderedDict()
    noun_counter = 0
    for tweet in tweets:
        tokens = processor.tokenize(tweet.text)
        for token in tokens:
            if token.pos == 'Noun':
                noun_counter += 1
                if token.text in noun_usage_dict:
                    noun_usage_dict[token.text] += 1
                else:
                    noun_usage_dict[token.text] = 1
        print noun_counter
    for item in OrderedDict(sorted(noun_usage_dict.items(), key = lambda t:t[1], reverse=True)).items():
        print item[0], item[1]
if __name__ == '__main__':
    analyze()
