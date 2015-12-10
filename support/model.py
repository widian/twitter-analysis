#!/usr/bin/env python
# -*- coding:utf8 -*-

import datetime
from sqlalchemy import Integer, String, BigInteger, Column, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint

Base = declarative_base()

class TweetBase(object):
    __tablename__ = 'tweet'

    def __init__(self, id, text, user, created_at):
        self.id = id
        self.text = text
        self.user = user
        self.created_at = created_at

    id = Column(BigInteger, primary_key=True)
    text = Column(String(141), nullable=False)
    user = Column(BigInteger, nullable=False, index=True)
    retweet_owner = Column(BigInteger)
    retweet_origin = Column(BigInteger)
    created_at = Column(DateTime, nullable=False)
    collected_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    reply_to = Column(BigInteger)

class Tweet(Base):
    __tablename__ = 'tweet'

    def __init__(self, id, text, user, created_at):
        self.id = id
        self.text = text
        self.user = user
        self.created_at = created_at

    id = Column(BigInteger, primary_key=True)
    text = Column(String(141), nullable=False)
    user = Column(BigInteger, nullable=False, index=True)
    retweet_owner = Column(BigInteger)
    retweet_origin = Column(BigInteger)
    created_at = Column(DateTime, nullable=False)
    collected_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    reply_to = Column(BigInteger)

class ErrorTweet(Base):
    __tablename__ = 'error_tweet'

    def __init__(self, id, text, user, created_at):
        self.id = id
        self.text = text
        self.user = user
        self.created_at = created_at

    id = Column(BigInteger, primary_key=True)
    text = Column(String(141), nullable=False)
    user = Column(BigInteger, nullable=False)
    retweet_owner = Column(BigInteger)
    retweet_origin = Column(BigInteger)
    created_at = Column(DateTime, nullable=False)
    collected_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    reply_to = Column(BigInteger)
    search_id = Column(Integer, primary_key=True)

class User(Base):
    __tablename__ = 'user'

    AUTHORIZED = 1
    UNAUTHORIZED = 0

    def __init__(self, id, name, screen_name, statuses_count, follower_count):
        self.id = id
        self.name = name
        self.screen_name = screen_name
        self.statuses_count = statuses_count
        self.follower_count = follower_count

    id = Column(BigInteger, primary_key=True)
    name = Column(String(21), nullable=False)
    screen_name = Column(String(16), unique=True, nullable=False)
    statuses_count = Column(Integer, nullable=False)
    follower_count = Column(Integer, nullable=False)
    tweet_collected_date = Column(DateTime)
    created_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    language_type = Column(Integer)
    authorized = Column(Integer, nullable=False, default=AUTHORIZED)

class Celebrity(Base):
    __tablename__ = 'celebrity'

    def __init__(self, id, celebrity_type):
        self.id = id
        self.celebrity_type = celebrity_type
    #TODO : Make relationship with User. Use User information
    #TODO : Make relationship with CelebrityType. Use Celebrity Type information
    id = Column(BigInteger, primary_key=True)
    celebrity_type = Column(Integer, nullable=False)

class CelebrityType(Base):
    __tablename__ = 'celebrity_type'
    
    def __init__(self, celebrity_type, type_name):
        self.celebrity_type = celebrity_type
        self.type_name = type_name
    celebrity_type = Column(Integer, primary_key=True)
    type_name = Column(String(30), nullable=False)

    
class Relationship(Base):
    __tablename__ = 'relationship'

    def __init__(self, following, follower):
        self.following = following
        self.follower = follower

    id = Column(Integer, primary_key=True, autoincrement=True)
    following = Column(BigInteger, nullable=False)
    follower = Column(BigInteger, nullable=False)
    collected_date = Column(DateTime, nullable=False, default=datetime.datetime.now())

    relationship = UniqueConstraint('following', 'follower')

class RateLimit(Base):
    __tablename__ = 'rate_limit'

    def __init__(self, limit, process_name, minimum_max_id=None):
        self.limit = limit
        self.process_name = process_name
        self.minimum_max_id = minimum_max_id 

    id = Column(Integer, primary_key=True)
    limit = Column(DateTime, nullable=False)
    collected_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    process_name = Column(String(32), nullable=False)
    minimum_max_id = Column(BigInteger)

class LanguageType(Base):
    __tablename__ = 'language_type'

    def __init__(self, language_type, name):
        self.language_type = language_type 
        self.name = name

    language_type = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(45), nullable=False)

class TweetType(Base):
    __tablename__ = 'tweet_type'

    def __init__(self, 
            start_time=None, end_time=None, 
            follower_of=None, 
            contain_retweet=1, contain_english=1, contain_username_mentioned=1,
            contain_linked_tweet=1, least_tweet_per_user=0):
        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time
        if follower_of is not None:
            self.follower_of = follower_of

        self.contain_linked_tweet = contain_linked_tweet
        self.contain_username_mentioned = contain_username_mentioned
        self.contain_english = contain_english
        self.contain_retweet = contain_retweet
        self.least_tweet_per_user = least_tweet_per_user

    #TODO : Add more column for 두 어카운트를 동시에 팔로잉하는 계정의 트윗

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_time = Column(DateTime, nullable=False, default=datetime.datetime.now())

    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=False, default=datetime.datetime.now())

    follower_of = Column(BigInteger)
    contain_retweet = Column(Integer, default=1)
    contain_english = Column(Integer, default=1)
    contain_username_mentioned = Column(Integer, default=1)
    contain_linked_tweet = Column(Integer, default=1)
    least_tweet_per_user = Column(Integer, default=0)

class TweetSearchLog(Base):
    __tablename__ = 'tweet_search_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tweet_id = Column(BigInteger, nullable=False)
    tweet_type = Column(Integer, nullable=False)

    collected_time = Column(DateTime, nullable=False, default=datetime.datetime.now())

class Tweet_335204566_1(TweetBase, Base):
    __tablename__ = 'tweet_335204566_1'

    #Use like a memo
    MAXIMUM_created_at = '2011-07-28 16:38:12'

class Tweet_335204566_2(TweetBase, Base):
    __tablename__ = 'tweet_335204566_2'

class Tweet_335204566_3(TweetBase, Base):
    __tablename__ = 'tweet_335204566_3'

class Tweet_335204566_4(TweetBase, Base):
    __tablename__ = 'tweet_335204566_4'

#class Tweet_335204566_2(Tweet):
#    __tablename__ = 'tweet_335204566_2'
#
#Tweet_335204566 = list()
#Tweet_335204566.append(Tweet_335204566_1)
#Tweet_335204566.append(Tweet_335204566_2)
