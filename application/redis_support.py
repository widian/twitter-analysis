#!/usr/bin/env python
# -*- coding:utf8 -*-

import redis
REDIS_URL_CONFIG = "redis://h:p91di8krbhqtua66k6ktsrrs53s@ec2-54-235-152-160.compute-1.amazonaws.com:14039"
r = redis.from_url(REDIS_URL_CONFIG)

def redis_set(key, value, expire=None):
    """ key: string
        value: any value (not list, dict)
        expire: integer (seconds)
    """
    if expire is None:
        r.set(key, value)
    else:
        r.setex(key, value, expire)

def redis_get(key):
    return r.get(key)

def redis_ttl(key):
    return r.ttl(key)

def expire_lock_twitter_search():
    key = "rate-limit-search"
    redis_set(key, True, 60 * 15)
    return True

def exist_lock_twitter_search():
    key = "rate-limit-search"
    if redis_get(key):
        return True
    else:
        return False

def ttl_exist_lock_twitter_search():
    key = "rate-limit-search"
    if redis_get(key):
        return redis_ttl(key)
    else:
        return 0

def is_refreshed(collection, character):
    return r.sismember(collection, character)

def refresh_expire_set(collection, character, seconds):
    if r.sismember(collection, character):
        return False
    else:
        r.sadd(collection, character)
        r.expire(collection, seconds)
        return True

if __name__ == '__main__':
    print r.get("test")
    print r.sismember("testset", "1")
    pass
