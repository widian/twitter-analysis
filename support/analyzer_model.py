#!/usr/bin/env python
# -*- coding:utf8 -*-

from __future__ import print_function

from collections import OrderedDict

# NLP Processors
from twkorean import TwitterKoreanProcessor

from support.mysql_support import Session, AnalysisSession
from support.model import Tweet, User, TweetType, TweetSearchLog, Relationship, WordTable, WordAnalysisLog, UserList
from sqlalchemy import desc, and_
from sqlalchemy.sql import func

import datetime, time

class Word(object):
    word = None
    pos = None
    id = 0

    def __init__(self, word, pos, counter):
        self.word = word
        self.pos = pos
        self.id = counter

class AnalysisType(object):
    """ contained_linked_tweet : 0 - 링크가 포함된 트윗을 제외, 1 - 링크가 포함된 트윗을 검색, 2 - 링크가 포함된 트윗만 검색
        contain_english : 0 - 외국어권 유저로 추정되는 유저의 트윗을 제외, 1 - 외국어권 유저의 트윗을 검색, 2 - 외국어권 유저의 트윗만 검색
        contain_username_mentioned : 0 - 특정 유저에게 답변한 트윗을 제외, 1 - 특정 유저에게 답변한 트윗을 포함, 2 - 특정 유저에게 답변한 트윗만 검색
        contain_retweet : 0 - 리트윗을 제외, 1 - 리트윗한 트윗을 검색, 2 - 리트윗한 트윗만 검색
        least_tweet_per_user : 특정 유저가 least_tweet_per_user만큼의 트윗을 하지 않았다면 검색하지 않음.
        user_list_type : 0 - 모든 유저를 검색, not 0 - UserList를 확인해서 user_list_type와 같은 list_type값을 가진 user_id의 리스트에 속하는 유저들의 트윗을 검색

        follower_of : follower_of의 follower인 트윗만 검색
        since : since부터의 트윗만 검색
        until : until까지의 트윗만 검색
    """
    contain_linked_tweet = 1 
    contain_english= 1
    contain_username_mentioned = 1
    contain_retweet = 1
    least_tweet_per_user = 0
    user_list_type = 0

    follower_of = None
    since = None
    until = None
    def __init__(self, since=None, until=None, follower_of=None, 
            contain_linked_tweet=1, contain_username_mentioned=1, contain_english=1,
            contain_retweet=1, least_tweet_per_user=0, user_list_type=0):
        if not (isinstance(since, datetime.datetime) and isinstance(until, datetime.datetime)):
            raise Exception('since and until only accept datetime object')
        self.contain_retweet = contain_retweet
        self.contain_linked_tweet = contain_linked_tweet
        self.contain_username_mentioned = contain_username_mentioned
        self.contain_english = contain_english
        self.least_tweet_per_user = least_tweet_per_user
        self.since = since
        self.until = until
        self.follower_of = follower_of
        self.user_list_type = user_list_type 
    
    def add_filter_to_query(self, target_tweet_table, query):
        if self.since is not None:
            if self.since >= target_tweet_table.get_maximum_created_at():
                """ maximum of created time is older than since (minimum of search range > max(table))
                """
                return None 
            query = query.filter(target_tweet_table.created_at > self.since)
        if self.until is not None:
            if self.until < target_tweet_table.get_minimum_created_at():
                """ minimum of created time is older than until (maximum of search range < min(table))
                """
                return None
            query = query.filter(target_tweet_table.created_at < self.until)

        if self.contain_retweet == 0:
            query = query.filter(target_tweet_table.retweet_owner == None)
        elif self.contain_retweet == 2:
            query = query.filter(target_tweet_table.retweet_owner != None)

        if self.contain_username_mentioned == 0:
            query = query.filter(target_tweet_table.reply_to == None)
        elif self.contain_username_mentioned == 2:
            query = query.filter(target_tweet_table.reply_to != None)
        return query

    def get_tweet_list(self, target_tweet_table, session):
        query = session.query(target_tweet_table)
        query = self.add_filter_to_query(target_tweet_table, query)
        if query is None:
            return None
        print('SQL Start')
        start = time.time()
        if self.user_list_type != 0:
            """ UserList로부터 타겟이 되는 user_id 리스트를 받아서 해당 아이디의 트윗만 수집
            """
            subquery_userlist = session.query(UserList.user_id).filter(UserList.list_type == self.user_list_type).subquery()
            query = query.filter(target_tweet_table.user.in_(subquery_userlist))

        pre_tweets = query.all()
        print (('GET a tweet set from tweet table %s') % target_tweet_table.__tablename__)

        user_query = session.query(target_tweet_table.user)
        user_query = self.add_filter_to_query(target_tweet_table, user_query)
        if user_query is None:
            """ Useless Routine, but add for safety
            """
            return None
        sub_query_user_of_tweets = user_query.group_by(target_tweet_table.user).subquery()
        user_info = session.query(User).filter(User.id.in_(sub_query_user_of_tweets)).all()

        print ('GET a user info of tweet owner from user table %s, SQL End : %s sec' % (target_tweet_table, time.time() - start))
        tweet_count_dict = dict()
        for item in user_info:
            tweet_count_dict[item.id] = item.statuses_count

        follower_list = list()
        if self.follower_of is not None:
            follower_rows = session.query(Relationship).filter(Relationship.following == self.follower_of).all()
            for item in follower_rows:
                follower_list.append(item.follower)

        print ('GET a follower info from relationship table %s')
        processor = TwitterKoreanProcessor()
        result = list()
        for tweet in pre_tweets:
            tokens = processor.tokenize(tweet.text)
            pos_set = set([])
            for token in tokens:
                pos_set.add(token.pos)
            if self.contain_english == 0 and 'Noun' not in pos_set:
                continue
            elif self.contain_english == 2 and 'Noun' in pos_set:
                continue
            if self.contain_linked_tweet == 0 and 'URL' in pos_set:
                continue
            elif self.contain_linked_tweet == 2 and 'URL' not in pos_set:
                continue
            if self.follower_of is not None and tweet.user not in follower_list:
                continue
            if self.least_tweet_per_user != 0:
                if tweet.user not in tweet_count_dict:
                    raise Exception('Subquery, query ERROR!')
                else:
                    if tweet_count_dict[tweet.user] < self.least_tweet_per_user:
                        continue
            result.append(tweet)
        print ('Finish to make tweet list')
        return result 

    def make_query(self, session):
        query = session.query(TweetType)
        query = query.filter(TweetType.since == self.since)
        query = query.filter(TweetType.until == self.until)
        query = query.filter(TweetType.follower_of == self.follower_of)
        query = query.filter(TweetType.contain_retweet == self.contain_retweet)\
                       .filter(TweetType.contain_english == self.contain_english)\
                       .filter(TweetType.contain_username_mentioned == self.contain_username_mentioned)\
                       .filter(TweetType.contain_linked_tweet == self.contain_linked_tweet)\
                       .filter(TweetType.least_tweet_per_user == self.least_tweet_per_user)\
                       .filter(TweetType.user_list_type == self.user_list_type)
        return query 

    def get_type_id(self, session):
        type_row = self.make_query(session).first()
        if type_row is None:
            session.add(self.make_type_data())
            session.commit()
            type_row = self.make_query(session).first()
        return type_row.id


    def make_type_data(self):
        return TweetType(
                since=self.since, until=self.until, follower_of=self.follower_of,
                contain_retweet=self.contain_retweet, contain_english=self.contain_english,
                contain_username_mentioned=self.contain_username_mentioned, contain_linked_tweet=self.contain_linked_tweet,
                least_tweet_per_user=self.least_tweet_per_user,
                user_list_type=self.user_list_type)
            
    def __repr__(self): 
        return ("since : %s, until : %s, follower_of : %s, contain_retweet : %d, contain_english : %d, contain_username_mentioned : %d, contain_linked_tweet : %d, least_tweet_per_user : %d, user_list_type : %d" % (self.since, self.until, self.follower_of, self.contain_retweet, self.contain_english, self.contain_username_mentioned, self.contain_linked_tweet, self.least_tweet_per_user, self.user_list_type))

class UserListType(object):
    #TODO : 아직 미사용중. 코드보강 및 알고리즘 보강이 필요
    def make_userlist_id(self, sess):
        id = sess.query(func.max(UserList.list_type)).first()
        if id[0] is None:
            return 1
        else:
            return id[0]

    def add_user_list(self, sess, user_list):
        id = self.make_userlist_id(sess)
        for item in user_list:
            sess.add(UserList(item, id))
        sess.commit()
        return id

    def get_user_list(self, sess, list_type):
        user_list = sess.query(UserList).filter(UserList.list_type == list_type).all()
        return user_list

    def get_user_list_type(self, sess, user_list):
        #TODO : user list의 user_id를 순서대로 검사하여 해당 아이디가 속하는 list_type이 있으면 리턴
        #       만약 속하는 list_type이 있다면 user_list의 다음 id를 검사해서 겹치는 id가 있는지 확인
        #       전부 겹친다면 해당 type을 반환, 그렇지 않다면 None을 반환
        pass

class PrintString(object):
    def print_tokens(self, tokens, end="\n"):
        """ https://github.com/jaepil/twkorean
        """
        if isinstance(tokens, list):
            print("[", end="")
        elif isinstance(tokens, tuple):
            print("(", end="")

        for t in tokens:
            if t != tokens[-1]:
                elem_end = ", "
            else:
                elem_end = ""

            if isinstance(t, (list, tuple)):
                self.print_tokens(t, end=elem_end)
            else:
                print(t, end=elem_end)

        if isinstance(tokens, list):
            print("]", end=end)
        elif isinstance(tokens, tuple):
            print(")", end=end)

