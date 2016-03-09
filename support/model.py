#/usr/bin/env python
# -*- coding:utf8 -*-

import datetime
from sqlalchemy import Integer, String, BigInteger, Column, DateTime, Index, Unicode
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
    text = Column(String(255), nullable=False)
    user = Column(BigInteger, nullable=False)
    retweet_owner = Column(BigInteger)
    retweet_origin = Column(BigInteger)
    created_at = Column(DateTime, nullable=False)
    collected_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    reply_to = Column(BigInteger)
    search_id = Column(Integer, primary_key=True, default=-1)

class User(Base):
    __tablename__ = 'user'

    AUTHORIZED = 1
    UNAUTHORIZED = 0

    def __init__(self, user):
        self.update(user)

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode(21), nullable=False)
    screen_name = Column(Unicode(16), unique=True, nullable=False)
    statuses_count = Column(Integer, nullable=False)
    follower_count = Column(Integer, nullable=False)
    tweet_collected_date = Column(DateTime)
    updated_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    created_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    language_type = Column(Integer)
    authorized = Column(Integer, nullable=False, default=AUTHORIZED)
    protected = Column(Integer, nullable=False, default=0)

    def update(self, user):
        self.id = user.id
        self.name = user.name
        self.screen_name = user.screen_name
        self.statuses_count = user.statuses_count
        self.follower_count = user.followers_count
        self.updated_date = datetime.datetime.now()
        self.protected = user.protected

class UserDetail(Base):
    __tablename__ = 'user_detail'

    #NOTE : User에 있는 Column은 UserDetail에서 관리하지 않게 하기
    #NOTE : 그냥 UserDetail이 User에 있는 정보를 관리하도록할까. User의 정보는 업데이트 되고 있지 않기 때문에

    def __init__(self, user, created_at):
        self.update(user, created_at)

    id = Column(BigInteger, ForeignKey('user.id'), primary_key=True)

    user = relationship("User")

    """ Colors """
    profile_sidebar_fill_color = Column(Integer)
    profile_sidebar_border_color = Column(Integer)
    profile_link_color = Column(Integer)
    profile_text_color = Column(Integer)
    profile_background_color = Column(Integer)

    """ Booleans """
    profile_background_tile = Column(Integer, nullable=False)
    
    default_profile = Column(Integer, nullable=False)
    contributors_enabled = Column(Integer, nullable=False)
    protected = Column(Integer, nullable=False)
    geo_enabled = Column(Integer, nullable=False)
    verified = Column(Integer, nullable=False)
    notifications = Column(Integer)
    default_profile_image = Column(Integer, nullable=False)

    """ Else """
    """ http://stackoverflow.com/questions/5735242/proper-way-to-insert-strings-to-a-sqlalchemy-unicode-column
        Change String columns to Unicode columns
    """
    profile_image_url = Column(Unicode(256), nullable=False)
    location = Column(Unicode(80), nullable=False)
    created_at = Column(DateTime, nullable=False)
    favourites_count = Column(Integer, nullable=False)
    url = Column(Unicode(140))
    utc_offset = Column(Integer)
    listed_count = Column(Integer, nullable=False)
    lang = Column(Unicode(8), nullable=False)
    description = Column(Unicode(256), nullable=False)
    time_zone = Column(Unicode(40))
    profile_background_image_url = Column(Unicode(256))
    friends_count = Column(Integer, nullable=False)

    latest_status_id = Column(BigInteger)
    updated_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    created_time = Column(DateTime, nullable=False, default=datetime.datetime.now())

    def _color_to_int(self, color_string):
        """ http://stackoverflow.com/questions/209513/convert-hex-string-to-int-in-python
        """ 
        return int(color_string, 16)

    def color_to_string(self, color_int):
        """ http://stackoverflow.com/questions/16414559/trying-to-use-hex-without-0x
        """ 
        return "{:06X}".format(color_int)

    def update(self, user, created_at):
        self.id = user.id
        self.id_constraint = user.id

        """ Colors """
        self.profile_sidebar_fill_color = self._color_to_int(user.profile_sidebar_fill_color)
        self.profile_link_color = self._color_to_int(user.profile_link_color)
        self.profile_text_color = self._color_to_int(user.profile_text_color)
        self.profile_background_color = self._color_to_int(user.profile_background_color)

        """ Booleans """
        self.profile_background_tile = user.profile_background_tile
        self.default_profile = user.default_profile
        self.contributors_enabled = user.contributors_enabled
        self.protected = user.protected
        self.geo_enabled = user.geo_enabled
        self.verified = user.verified
        self.notifications = user.notifications
        self.default_profile_image = user.default_profile_image

        """ Else """
        self.profile_image_url = user.profile_image_url
        self.location = user.location
        self.favourites_count = user.favourites_count
        self.url = user.url
        self.utc_offset = user.utc_offset
        self.listed_count = user.listed_count
        self.lang = user.lang
        self.description = user.description
        self.time_zone = user.time_zone
        self.profile_background_image_url = user.profile_background_image_url
        self.friends_count = user.friends_count

        if user.status is not None:
            self.latest_status_id = user.status.id
        else:
            self.latest_status_id = None

        self.created_at = created_at
        self.updated_time = datetime.datetime.now()

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
    user_id = Column(Integer, nullable=False)
    
    
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
            contain_linked_tweet=1, least_tweet_per_user=0, user_list_type=0):
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
        self.user_list_type = user_list_type

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

    def __init__(self, user_id, list_type):
        self.user_id = user_id
        self.list_type = list_type 

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
    """ pos : part-of-speech
        http://www.cs.cmu.edu/~ark/TweetNLP/#pos
    """ 
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
    search_log_type = Column(Integer, ForeignKey('tweet_type.id'), nullable=False, index=True)
    tweet_type = relationship("TweetType")
    word_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now())


class Tweet_335204566_1(TweetBase, Base):
    __tablename__ = 'tweet_335204566_1'

    _MINIMUM_id = 621106947786289153
    _MINIMUM_created_at = '2015-07-15 00:00:10'
    _MAXIMUM_id = 679220176424984576
    _MAXIMUM_created_at = '2015-12-22 08:41:24'

class Tweet_335204566_2(TweetBase, Base):
    __tablename__ = 'tweet_335204566_2'

    _MINIMUM_id = 679220181642715136
    _MINIMUM_created_at = '2015-12-22 08:41:25'
    _MAXIMUM_id = 698760147024252928
    _MAXIMUM_created_at = '2016-02-14 06:46:16'

class Tweet_281916923_1(TweetBase, Base):
    __tablename__ = 'tweet_281916923_1'

    _MINIMUM_id = 621106964530003968
    _MINIMUM_created_at = '2015-07-15 00:00:14'
    _MAXIMUM_id = 693712458821668864
    _MAXIMUM_created_at = '2016-01-31 08:28:33'

class Tweet_281916923_2(TweetBase, Base):
    __tablename__ = 'tweet_281916923_2'

    _MINIMUM_id = 693712517193867273
    _MINIMUM_created_at = '2016-01-31 08:28:47'
    _MAXIMUM_id = 700096408263593986
    _MAXIMUM_created_at = '2016-02-17 23:16:05'



Tweet_335204566 = list()
Tweet_335204566.append(Tweet_335204566_1)
Tweet_335204566.append(Tweet_335204566_2)

Tweet_281916923 = list()
Tweet_281916923.append(Tweet_281916923_1)
Tweet_281916923.append(Tweet_281916923_2)

Tweet_44771983 = list()
#Tweet_44771983.append(Tweet_44771983_1)
#Tweet_44771983.append(Tweet_44771983_2)
#Tweet_44771983.append(Tweet_44771983_3)
#
Tweet_155884548 = list()
#Tweet_155884548.append(Tweet_155884548_1)
#Tweet_155884548.append(Tweet_155884548_2)
#Tweet_155884548.append(Tweet_155884548_3)
#Tweet_155884548.append(Tweet_155884548_4)
#Tweet_155884548.append(Tweet_155884548_5)
#Tweet_155884548.append(Tweet_155884548_6)
#Tweet_155884548.append(Tweet_155884548_7)
#Tweet_155884548.append(Tweet_155884548_8)
#Tweet_155884548.append(Tweet_155884548_9)
#Tweet_155884548.append(Tweet_155884548_10)


if __name__ == '__main__':
    pass
