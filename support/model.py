#!/usr/bin/env python
# -*- coding:utf8 -*-

import datetime
from sqlalchemy import Integer, String, BigInteger, Column, DateTime, Index
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint

Base = declarative_base()

class TweetBase(object):
    __tablename__ = 'tweet'

    _MAXIMUM_created_at = None
    _MAXIMUM_id = None

    def __init__(self, id, text, user, created_at):
        self.id = id
        self.text = text
        self.user = user
        self.created_at = created_at

    @classmethod
    def get_maximum_id(cls):
        return cls._MAXIMUM_id

    @classmethod
    def get_minimum_id(cls):
        return cls._MINIMUM_id

    @classmethod
    def get_maximum_created_at(cls):
        return datetime.datetime.strptime(cls._MAXIMUM_created_at, '%Y-%m-%d %H:%M:%S')

    @classmethod
    def get_minimum_created_at(cls):
        return datetime.datetime.strptime(cls._MINIMUM_created_at, '%Y-%m-%d %H:%M:%S')
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
        #NOTE : NOT IMPLEMENTED IN DATABASE
        raise Exception("NOT IMPLEMENTED IN DATABASE")

        self.id = id
        self.celebrity_type = celebrity_type
    #TODO : Make relationship with User. Use User information
    #TODO : Make relationship with CelebrityType. Use Celebrity Type information
    id = Column(BigInteger, primary_key=True)
    celebrity_type = Column(Integer, nullable=False)

class CelebrityType(Base):
    __tablename__ = 'celebrity_type'
    
    def __init__(self, celebrity_type, type_name):
        #NOTE : NOT IMPLEMENTED IN DATABASE
        raise Exception("NOT IMPLEMENTED IN DATABASE")
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
            since=None, until=None, 
            follower_of=None, 
            contain_retweet=1, contain_english=1, contain_username_mentioned=1,
            contain_linked_tweet=1, least_tweet_per_user=0):
        if since is not None:
            self.since = since
        if until is not None:
            self.until = until
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

    since = Column(DateTime)
    until = Column(DateTime, nullable=False, default=datetime.datetime.now())

    follower_of = Column(BigInteger)
    contain_retweet = Column(Integer, default=1)
    contain_english = Column(Integer, default=1)
    contain_username_mentioned = Column(Integer, default=1)
    contain_linked_tweet = Column(Integer, default=1)
    least_tweet_per_user = Column(Integer, default=0)
    user_list_type = Column(Integer, default=None)

class UserList(Base):
    __tablename__ = 'user_list'

    def __init__(self, user_id, search_type):
        self.user_id = user_id
        self.search_type = search_type

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    list_type = Column(Integer, nullable=False)
    created_time = Column(DateTime, nullable=False, default=datetime.datetime.now())


class TweetSearchLog(Base):
    __tablename__ = 'tweet_search_log'

    def __init__(self, tweet_id, tweet_type):
        self.tweet_id = tweet_id
        self.tweet_type = tweet_type
    id = Column(Integer, primary_key=True, autoincrement=True)
    tweet_id = Column(BigInteger, nullable=False)
    tweet_type = Column(Integer, nullable=False)

    collected_time = Column(DateTime, nullable=False, default=datetime.datetime.now())

class WordTable(Base):
    __tablename__ = 'word_table'
    
    def __init__(self, word, pos, unknown):
        self.word = word
        self.pos = pos
        self.unknown = unknown

    #TODO : change pos to interger type value, and make pos table to reduce querying weight
    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(140), nullable=False)
    pos = Column(String(16), nullable=False)
    unknown = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now())

class WordAnalysisLog(Base):
    __tablename__ = 'word_analysis_log'

    def __init__(self, word_id, word_count, search_log_type):
        self.word_id = word_id
        self.word_count = word_count
        self.search_log_type = search_log_type

    id = Column(Integer, primary_key=True, autoincrement=True)
    word_id = Column(Integer, ForeignKey('word_table.id'), nullable=False)
    word = relationship("WordTable")
    search_log_type = Column(Integer, ForeignKey('tweet_type.id'), nullable=False)
    tweet_type = relationship("TweetType")
    word_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now())


class Tweet_335204566_1(TweetBase, Base):
    __tablename__ = 'tweet_335204566_1'

    #Use like a memo
    _MINIMUM_id = 14251891
    _MINIMUM_created_at = '2007-03-28 13:21:41'
    _MAXIMUM_id = 96620479451906048
    _MAXIMUM_created_at = '2011-07-28 16:38:12'

class Tweet_335204566_2(TweetBase, Base):
    __tablename__ = 'tweet_335204566_2'

    _MINIMUM_id = 96620695978643456
    _MINIMUM_created_at = '2011-07-28 16:39:03'
    _MAXIMUM_id = 187823936057262080
    _MAXIMUM_created_at = '2012-04-05 08:48:10'

class Tweet_335204566_3(TweetBase, Base):
    __tablename__ = 'tweet_335204566_3'

    _MINIMUM_id = 187823967489376256
    _MINIMUM_created_at = '2012-04-05 08:48:18'
    _MAXIMUM_id = 275429499905118208
    _MAXIMUM_created_at = '2012-12-03 02:41:24'

class Tweet_335204566_4(TweetBase, Base):
    __tablename__ = 'tweet_335204566_4'

    _MINIMUM_id = 275429574492426240
    _MINIMUM_created_at = '2012-12-03 02:41:42'
    _MAXIMUM_id = 367339079869808640
    _MAXIMUM_created_at = '2013-08-13 17:37:16'

class Tweet_335204566_5(TweetBase, Base):
    __tablename__ = 'tweet_335204566_5'

    _MINIMUM_id = 367339336745750528
    _MINIMUM_created_at = '2013-08-13 17:38:17'
    _MAXIMUM_id = 471998072784834561
    _MAXIMUM_created_at = '2014-05-29 12:54:44'

class Tweet_335204566_6(TweetBase, Base):
    __tablename__ = 'tweet_335204566_6'

    _MINIMUM_id = 471998203177365506
    _MINIMUM_created_at = '2014-05-29 12:55:15'
    _MAXIMUM_id = 556243889950957568
    _MAXIMUM_created_at = '2015-01-17 00:17:32'

class Tweet_335204566_7(TweetBase, Base):
    __tablename__ = 'tweet_335204566_7'

    _MINIMUM_id = 556243972167720960
    _MINIMUM_created_at = '2015-01-17 00:17:52'
    _MAXIMUM_id = 621310510785409024
    _MAXIMUM_created_at = '2015-07-15 13:29:03'

class Tweet_335204566_8(TweetBase, Base):
    __tablename__ = 'tweet_335204566_8'

    _MINIMUM_id = 621310521631838208
    _MINIMUM_created_at = '2015-07-15 13:29:06'
    _MAXIMUM_id = 658478158061039616
    _MAXIMUM_created_at = '2015-10-26 03:00:01'

class Tweet_335204566_9(TweetBase, Base):
    __tablename__ = 'tweet_335204566_9'

    _MINIMUM_id = 658478161550815232
    _MINIMUM_created_at = '2015-10-26 03:00:02'
    _MAXIMUM_id = 673675443527020544
    _MAXIMUM_created_at = '2015-12-07 01:28:36'

class Tweet_281916923_1(TweetBase, Base):
    __tablename__ = 'tweet_281916923_1'

    _MINIMUM_created_at = '2015-07-15 00:00:03'
    _MINIMUM_id = 621106918325497856
    _MAXIMUM_created_at = '2015-12-17 07:37:34'
    _MAXIMUM_id = 677392173583601664

class Tweet_44771983_1(TweetBase, Base):
    __tablename__ = 'tweet_44771983_1'

    _MINIMUM_created_at = '2015-07-15 00:00:30'
    _MINIMUM_id = 621107030376321028
    _MAXIMUM_created_at = '2015-12-16 06:01:20'
    _MAXIMUM_id = 677005569400639489

class Tweet_44771983_2(TweetBase, Base):
    __tablename__ = 'tweet_44771983_2'

    _MINIMUM_created_at = '2015-12-16 06:01:23'
    _MINIMUM_id = 677005581903884292
    _MAXIMUM_created_at = '2015-12-24 16:06:08'
    _MAXIMUM_id = 680056873668620289

Tweet_335204566 = list()
Tweet_335204566.append(Tweet_335204566_1)
Tweet_335204566.append(Tweet_335204566_2)
Tweet_335204566.append(Tweet_335204566_3)
Tweet_335204566.append(Tweet_335204566_4)
Tweet_335204566.append(Tweet_335204566_5)
Tweet_335204566.append(Tweet_335204566_6)
Tweet_335204566.append(Tweet_335204566_7)
Tweet_335204566.append(Tweet_335204566_8)
Tweet_335204566.append(Tweet_335204566_9)

Tweet_281916923 = list()
Tweet_281916923.append(Tweet_281916923_1)

Tweet_44771983 = list()
Tweet_44771983.append(Tweet_44771983_1)
Tweet_44771983.append(Tweet_44771983_2)

if __name__ == '__main__':
    datetime.datetime.strptime("2015-07-15 13:29:03", '%Y-%m-%d %H:%M:%S')
    print datetime.date(year=1970, month=1, day=1)
