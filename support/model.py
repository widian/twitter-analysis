#!/usr/bin/env python
# -*- coding:utf8 -*-

import datetime
from sqlalchemy import Integer, String, BigInteger, Column, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tweet(Base):
    __tablename__ = 'tweet'

    def __init__(self, id, text, user, created_at):
        self.id = id
        self.text = text
        self.user = user
        self.created_at = created_at
        self.collected_date = datetime.datetime.now()

    id = Column(BigInteger, primary_key=True)
    text = Column(String(140), nullable=False)
    user = Column(BigInteger, nullable=False)
    retweet_owner = Column(BigInteger)
    retweet_origin = Column(BigInteger)
    created_at = Column(DateTime, nullable=False)
    collected_date = Column(DateTime, nullable=False)
    reply_to = Column(BigInteger)

class User(Base):
    __tablename__ = 'user'

    def __init__(self, id, screen_name, statuses_count):
        self.id = id
        self.screen_name = screen_name
        self.statuses_count = statuses_count
        self.collected_date = datetime.datetime.now()

    id = Column(BigInteger, primary_key=True)
    screen_name = Column(String(16), unique=True)
    statuses_count = Column(Integer)
    collected_date = Column(DateTime, nullable=False)
    
class Relationship(Base):
    __tablename__ = 'relationship'

    def __init__(self, following, follower):
        self.following = following
        self.follower = follower
        self.collected_date = datetime.datetime.now()

    id = Column(Integer, primary_key=True, autoincrement=True)
    following = Column(BigInteger, nullable=False)
    follower = Column(BigInteger, nullable=False)
    collected_date = Column(DateTime, nullable=False)

class RateLimit(Base):
    __tablename__ = 'rate_limit'

    def __init__(self, limit, process_name, minimum_max_id=None):
        self.limit = limit
        self.process_name = process_name
        self.minimum_max_id = minimum_max_id 
        self.collected_date = datetime.datetime.now()

    id = Column(Integer, primary_key=True)
    limit = Column(DateTime, nullable=False)
    collected_date = Column(DateTime, nullable=False)
    process_name = Column(String(32), nullable=False)
    minimum_max_id = Column(BigInteger)

