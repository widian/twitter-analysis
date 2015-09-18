import redis
REDIS_URL_CONFIG = "redis://h:p91di8krbhqtua66k6ktsrrs53s@ec2-54-235-152-160.compute-1.amazonaws.com:14039"
r = redis.from_url(REDIS_URL_CONFIG)

def redis_set(key, value, expire):
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

def lock_twitter_search():
    key = "on-search"
    if redis_get(key):
        return False
    else:
        redis_set(key, True)
        return True

def unlock_twitter_search():
    key = "on-search"
    if redis_get(key):
        redis_set(key, False)
        return True
    else:
        return False

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
