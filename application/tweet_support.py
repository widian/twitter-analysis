#!/usr/bin/env python
# -*- coding:utf8 -*-
from TwitterSearch import *
import datetime
from email.utils import parsedate_tz

class MyTwitterSearchOrder(TwitterSearchOrder):
    def set_since(self, date):
        """ Sets 'since' parameter used to return \
        only tweets generated after the given date

        :param date : A datetime instance
        :raises: TwitterSearchException
        """

        if isinstance(date, datetime.date) and date <= datetime.date.today():
            self.arguments.update({'since': '%s' % date.strftime('%Y-%m-%d')})
        else:
            raise TwitterSearchException(1007)

class TweetSearchSupport(object):
    ts = None
    def __init__(self):
        self.ts = TwitterSearch(
                consumer_key = 'Jn0vFPTkewSek85vb1USoCQf4',
                consumer_secret = 'VnFh6AvyiojNKVFUryQXWaKKzHsvBsVnebjQWDcOCfftsjgO9J',
                access_token = '100506002-67IOcA0mZehNVmJlqmkOIB4QsJfjlXKK1OX0ylqO',
                access_token_secret = 'j72a7volEPzuwRAmu44j467IyxdZHpgIA1fPxU6AgWDy1')
    def get_ts(self):
        return self.ts

    def generate_tso(self, name_list, start_date, or_operator=False):
        """ name_list : 트위터 검색에 사용할 검색어들의 리스트
            start_date : 트위터 검색이 시작되는 날짜 (GMT 0000 기준)
        """
        tso = MyTwitterSearchOrder()
#        tso = TwitterUserOrder('lys2419') # create a TwitterUserOrder to access specific user timeline
#        for tweet in ts.search_tweets_iterable(tso):
#            tweet_text = ('%s @%s tweeted: %s' % (tweet['created_at'], tweet['user']['screen_name'], tweet['text']))
#            print tweet_text
        tso.set_keywords(name_list, or_operator=or_operator)
        tso.set_language('ko')
        tso.set_include_entities(False)
        tso.set_since(start_date - datetime.timedelta(days=8))
        tso.set_until(start_date - datetime.timedelta(days=1))
        return tso

    def to_datetime(self, datestring):
        """ referenced
        http://stackoverflow.com/questions/7703865/going-from-twitter-date-to-python-datetime-date
        """
        time_tuple = parsedate_tz(datestring.strip())
        dt = datetime.datetime(*time_tuple[:6])
        return dt - datetime.timedelta(seconds=time_tuple[-1])

if __name__ == '__main__':
    import charcollection
    character = charcollection.cinde_characters[0]
    tss = TweetSearchSupport()
    today = datetime.datetime.now().date()
    tso = tss.generate_tso(character.encode('UTF-8'), today)
    ts = tss.get_ts()
    for tweet in ts.search_tweets_iterable(tso):
        tweet_text = ('%s @%s tweeted: %s' % (tweet['created_at'], tweet['user']['screen_name'], tweet['text']))
        print tweet_text

