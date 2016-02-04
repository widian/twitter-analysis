#!/usr/bin/env python
# -*- coding:utf8 -*-

import datetime, re
from email.utils import parsedate_tz
from HTMLParser import HTMLParser

from twitter import TwitterError 

from support.tweet_support import TweetSupport, TweetErrorHandler, ErrorNumbers
from support.mysql_support import Session
from support.model import RateLimit, User, Tweet, ErrorTweet, Relationship, UserDetail

from sqlalchemy.exc import DataError
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

class Crawler(object):
    ts = None
    api = None
    hparser = None
    process_name = None
    def __init__(self):
        self.ts = TweetSupport()
        self.api = self.ts.get_api()
        self.hparser = HTMLParser()

    def crawling(self, user_id, authorized=User.AUTHORIZED, **kwargs):
        #TODO : NEED TO RAISE NOT IMPLEMENTED ERROR
        print "NOT IMPLEMENTED CRAWLING FUNCTION"
        return False
    
    def parse_ignore(self, text):
        """ referenced from
            http://stackoverflow.com/questions/26568722/remove-unicode-emoji-using-re-in-python
        """
        myre = None
        try:
            # Wide UCS-4 build
            myre = re.compile(u'['
                    u'\U0001F004'
                    u'\U0001F0CF'
                    u'\U0001F300-\U0001F6FF'
                    u'\U0001F140-\U0001F251'
                    u'\U0001F910-\U0001F9C0'
                    u'\U000FE000-\U000FECFF'
                    u'\u24c2'
                    u'\u2702-\u27B0'
                    u'\u2600-\u26FF\u2700-\u27BF]+', 
# 여기까지 이모티콘
                    re.UNICODE)
        except re.error:
            # Narrow UCS-2 build
            #\ud800\udd00 - \ud800\uddff > \U00010100-\U000101FF
            #\ud83c\udf00 - \ud83d\ude4f > \U0001F300-\U0001F6FF
            #\ud83d\ude80 - \ud83d\udef3 > \U0001F680-\U0001F6F3
            #\ud83c\udd40 - \ud83c\ude51 > \U0001F140-\U0001F251
            #\ud83e\udd10 - \ud83e\uddc0 > \U0001F910-\U0001F9C0
            #\udb82\udc00 - \udb82\udcff > \U000F0800-\U000F08FF
            #\udbb8\udc00 - \udbbb\udcff > \U000FE000-\U000FECFF
            #IGNORING ALL 4 bytes UTF-8 string to use in MYSQL.
            #\ud800\udc00 - \udbff\udfff > \U00010000-\U0010FFFF
            """ 일본어에 사용시 참고 문헌 4byte UTF-8 한자 문제 (3, 4 수준) 
                https://www.softel.co.jp/blogs/tech/archives/596 
            """
            myre = re.compile(u'('
                    u'[\ud800-\udbff][\udc00-\udfff]|'
                    u'[\u2026\u24c2]|'
                    u'[\u2600-\u27BF]'
                    ')+',
                    re.UNICODE)
        text = self.hparser.unescape(text)
        return myre.sub('', text)

    def trim_newline(self, text):
        myre = re.compile(u'[\n]+')
        text = myre.sub(' ', text)
        text = re.sub(r'http[s]?:\/\/.*[\r\n]*', 'http://t.co/???', text, flags=re.MULTILINE)
        return re.sub(' +', ' ', text)

    def get_rate_limit_status(self):
        try:
            return self.api.GetRateLimitStatus()
        except TwitterError as e:
            # NOTE NOTE NOTE NOTE
            # 아마도 RateLimitStatus까지 RateLimit에 걸린 상황에 해당 루틴으로 들어올 가능성 높음
            # 해당 경우에는 모든 프로세스를 종료하고 로그를 남기는방향이
            print e

    def rate_limit_handler(self, case, 
            process_name=None, 
            minimum_max_id=None,
            **kwargs):
        sess = Session()
        cached_rate_limit = sess.query(RateLimit) \
                                .filter(RateLimit.process_name == process_name) \
                                .filter(RateLimit.limit > datetime.datetime.now()).first()
        wait_until = None
        if cached_rate_limit is not None:
            """ Rate Limit가 일어났을 때의 Handling을 Crawler가 담당하는게 아닌 
                Crawler의 클래스를 활용하는 외부 클래스가 시행하도록 수정함
            """
            print "wait to", cached_rate_limit.limit
            wait_until = cached_rate_limit.limit
        else:
            rate_limit = self.get_rate_limit_status()
            items = process_name.split('/')
            target_dict = rate_limit['resources'][items[1]][process_name]
            limit_since = datetime.datetime.fromtimestamp(int(target_dict['reset']))
            sess.add(RateLimit(limit_since, process_name, minimum_max_id=minimum_max_id))
            sess.commit()
            print "wait to", limit_since
            wait_until = limit_since
        sess.close()
        return (wait_until - datetime.datetime.now() ).total_seconds()

    def to_datetime(self, datestring):
        """ referenced from
            http://stackoverflow.com/questions/7703865/going-from-twitter-date-to-python-datetime-date
        """
        time_tuple = parsedate_tz(datestring.strip())
        dt = datetime.datetime(*time_tuple[:6])
        return dt - datetime.timedelta(seconds=time_tuple[-1])

    def get_user_info(self, screen_name=None, user_id=None, **kwargs):
        """ 만약 해당 유저정보가 이미 저장되어있다면
        """
        sess = Session()
        exist = sess.query(User).filter(or_(User.screen_name == screen_name,
                                            User.id == user_id)).first()

        #TODO : authorized값을 없애고 protected로 교체해야 함.
        if exist:
            """ 세션을 닫고 해당 유저의 id를 추가로 전달. screen_name을 받든, user_id를 받든
                crawling 함수에는 user_id를 전달함
            """
            sess.close()
            return exist.id, exist.authorized
        else:
            """ Twitter로부터 유저정보를 받은 뒤 DB에 저장.
                NOTE: 에러 처리 파트를 함수 바깥으로 빼놓고 처리하기.
            """
            ts = TweetSupport()
            api = ts.get_api()
            user = api.GetUser(screen_name=screen_name, user_id=user_id,
                                include_entities=kwargs['include_entities'] if 'include_entities' in kwargs else None)
            user_chunk = User(user)
            sess.add(user_chunk)
            sess.commit()
            sess.close()
            return user.id, 

    #TODO : 유저의 가장 최근 status 정보를 받아서 func에 정보를 전달하기
    def user_info( func ):
        """ 특정 crawling이 어떤 user대상이라면, 미리 user정보를 받아오기 위한
            decorator함수. 
        """
        def db_user(self, screen_name=None, user_id=None, **kwargs):
            process_name = "/users/show/:id"
            try:
                result = self.get_user_info(screen_name=screen_name, user_id=user_id, **kwargs)
                if len(result) > 1:
                    return func(self, result[0], authorized=result[1], **kwargs)
                else:
                    return func(self, result[0], **kwargs)
            except TwitterError as e:
                """ Error처리는 다른 함수와 동일
                """
                sess = Session()
                t = TweetErrorHandler(e)
                t.add_handler(ErrorNumbers.RATE_LIMIT_ERROR, self.rate_limit_handler)
                result = t.invoke(process_name=process_name)
                sess.commit()
                sess.close()
                return result 
        return db_user
    user_info = staticmethod(user_info)
   
    def user_list_info( func ):
        def get_user_list_info(self, listof_screen_name=None, listof_user_id=None, **kwargs):
            process_name = "/users/show/:id"
            try:
                user_list = list()
                if listof_screen_name is None:
                    for item in listof_user_id:
                        user_id = self.get_user_info(user_id=item)[0]
                        user_list.append(user_id)
                elif listof_user_id is None:
                    raise Exception('Unknown Input')
                else:
                    for item in listof_screen_name:
                        user_id = self.get_user_info(screen_name=item)[0]
                        user_list.append(user_id)
            except TwitterError as e:
                """ Error처리는 다른 함수와 동일
                """
                sess = Session()
                t = TweetErrorHandler(e)
                t.add_handler(ErrorNumbers.RATE_LIMIT_ERROR, self.rate_limit_handler)
                result = t.invoke(process_name=process_name)
                sess.commit()
                sess.close()
                return result 
            return func(self, user_list, **kwargs)
        return get_user_list_info
    user_list_info = staticmethod(user_list_info)

class UserTimelineCrawler(Crawler):
    minimum_max_id = None
    def __init__(self):
        Crawler.__init__(self)
        self.process_name = '/statuses/user_timeline'
    
    @Crawler.user_info
    def crawling(self, user_id, authorized=User.AUTHORIZED, since=datetime.date(year=1970, month=1, day=1), **kwargs):
        # sess => session
        sess = None
        if authorized == User.UNAUTHORIZED:
            print "Cannot Crawling Unauthorized User : ", user_id
            return True
        try:
            sess = Session()
            cached_maximum_id = None
            while True:
                # This routine must be shutdowned when result doesn't exist.
                statuses = self.api.GetUserTimeline(
                        user_id=user_id,
                        count=200,
                        max_id=self.minimum_max_id,
                        since_id=kwargs['since_id'] if 'since_id' in kwargs else None,
                        include_rts=kwargs['include_rts'] if 'include_rts' in kwargs else None,
                        trim_user=kwargs['trim_user'] if 'trim_user' in kwargs else None,
                        exclude_replies=kwargs['exclude_replies'] if 'exclude_replies' in kwargs else None
                )
                self.minimum_max_id = None
                if cached_maximum_id is None:
                    cached_row = sess.query(func.max(Tweet.id)).filter(Tweet.user == user_id).first()
                    if cached_row[0] is None:
                        cached_maximum_id = 0
                    else:
                        """ cache에서 가지고 있는 maximum id를 새 maximum_id로 지정해줌. 
                        """
                        cached_maximum_id = cached_row[0]
                passed_since = False
                for tweet in statuses:
                    self.minimum_max_id = tweet.id
                    if self.to_datetime(tweet.created_at) < datetime.datetime.combine(since, datetime.datetime.min.time()):
                        passed_since = True
                        break
                    if cached_maximum_id < tweet.id:
                        text = self.parse_ignore(tweet.text)
                        if len(text) > 140:
                            text = self.trim_newline(text)
                        tweet_chunk = Tweet(
                            tweet.id,
                            text,
                            tweet.user.id,
                            self.to_datetime(tweet.created_at))
                        if tweet.retweeted_status:
                            tweet_chunk.retweet_owner = tweet.retweeted_status.user.id
                            tweet_chunk.retweet_origin = tweet.retweeted_status.id
                        if tweet.in_reply_to_user_id:
                            tweet_chunk.reply_to = tweet.in_reply_to_user_id
                        sess.add(tweet_chunk)
                    """ print tweet search result (Unnecessary)
                    """
                    tweet_text = ('%s %s @%s tweeted: %s' % (tweet.id, tweet.created_at, tweet.user.screen_name, tweet.text))
                if passed_since:
                    break

                if self.minimum_max_id is None:
                    """ No result with self.api.GetUserTimeline
                    """
                    break
                else:
                    """ 만약 캐시된 tweet_id의 maximum이 이번 검색에서 얻은 minimum_id보다 작다면
                    """
                    if cached_maximum_id > self.minimum_max_id:
                        cached_row = sess.query(func.min(Tweet.id)).filter(Tweet.user == user_id).first()
                        if cached_row[0] < self.minimum_max_id:
                            self.minimum_max_id = cached_row[0]
                    """ 최종에는 - 1
                    """
                    self.minimum_max_id -= 1
            try:
                sess.commit()
            except DataError, exc:
                """ Mysql Error Handling for
                    트윗이 이모티콘, 조합형 한글, 확장형 한자 등으로 인해
                    UCS-2 python환경에서 140자가 넘은 것으로 인식될 때 따로 저장시키는 용도
                """
                sess.rollback()
                count = 0
                for item in exc.params:
                    if len(item[1]) > 140:
                        error_tweet = ErrorTweet(
                                item[0],
                                item[1],
                                item[2],
                                item[5])
                        sess.add(error_tweet)
                    else:
                        tweet = Tweet(
                                item[0],
                                item[1],
                                item[2],
                                item[5])
                        sess.add(tweet)
                    count += 1
                sess.commit()
            target_user = sess.query(User).filter(User.id == user_id).first()
            target_user.tweet_collected_date = datetime.datetime.now()
            sess.commit()
            sess.close()
            return True
        except TwitterError as e:
            t = TweetErrorHandler(e)
            t.add_handler(ErrorNumbers.RATE_LIMIT_ERROR, self.rate_limit_handler)
            t.add_handler(ErrorNumbers.NOT_AUTHORIZED, self.not_authorized_handler)
            result = t.invoke(process_name=self.process_name, minimum_max_id=self.minimum_max_id, user_id=user_id)
            if sess is not None:
                sess.commit()
                sess.close()
            return result 

    def not_authorized_handler(self, case,
            user_id=None, **kwargs):
        if user_id is None:
            """ user_id must be required
            """
            print "User ID Require!"
            return None
        sess = Session()
        target_user = sess.query(User).filter(User.id == user_id).first()
        target_user.authorized = User.UNAUTHORIZED
        sess.commit()
        sess.close()


class UserFollowerIDs(Crawler):
    def __init__(self):
        Crawler.__init__(self)
        self.process_name = '/followers/ids'

    @Crawler.user_info
    def crawling(self, user_id, **kwargs):
        sess = None
        try:
            ts = TweetSupport()
            api = ts.get_api()
            follower_ids = api.GetFollowerIDs(
                    user_id=user_id,
                    cursor=kwargs['cursor'] if 'cursor' in kwargs else None,
                    stringify_ids=kwargs['stringify_ids'] if 'stringify_ids' in kwargs else None,
                    count=kwargs['count'] if 'count' in kwargs else None,
                    total_count=kwargs['total_count'] if 'total_count' in kwargs else None)
            sess = Session()
            remained = len(follower_ids)
            for id in follower_ids:
                remained -= 1
                print "add ", remained
                exist = sess.query(Relationship).filter(Relationship.following == user_id).filter(Relationship.follower == id).first()
                if exist:
                    continue
                else:
                    relationship_chunk = Relationship(
                            user_id,
                            id)
                    sess.add(relationship_chunk)
            sess.commit()
            sess.close()
            return True
        except TwitterError as e:
            t = TweetErrorHandler(e)
            t.add_handler(ErrorNumbers.RATE_LIMIT_ERROR, self.rate_limit_handler)
            result = t.invoke(process_name=self.process_name)
            if sess is not None:
                sess.commit()
                sess.close()
            return result 

#class StatusCrawler(Crawler):
#    
#    def __init__(self):
#        Crawler.__init__(self)
#        self.process_name = '/statuses/lookup'
#
#    def crawling(self, id_list):
#        statuses = self.api.GetStatusLookup(
#                id="20, 432656548536401920")
#        for stat in statuses:
#            print stat
#

class UserLookupCrawler(Crawler):
    def __init__(self):
        Crawler.__init__(self)
        self.process_name = '/statuses/lookup'
    
    @Crawler.user_list_info
    def crawling(self, listof_user_id, update=False, **kwargs):
        sess = None
        try:
            ts = TweetSupport()
            api = ts.get_api()
            user_list = api.UsersLookup(
                    user_id=listof_user_id,
                    include_entities=kwargs['include_entities'] if 'include_entities' in kwargs else None)
            sess = Session()
            if update:
                for item in user_list:
                    #TODO : Lookup에서 정보보기를 요청했는데, 정보가 오지 않은 아이디를 정보수집 불가능 아이디로 판단하고, 제거하는 기능이 필요함
                    user_row = sess.query(User).filter(User.id == item.id).first()
                    """ update모드이면, User 테이블의 row를 수정함.
                    """
                    user_row.update(item)

                    row = sess.query(UserDetail).filter(UserDetail.id == item.id).first()
                    if row is None:
                        user_chunk = UserDetail(item, self.to_datetime(item.created_at))
                        sess.add(user_chunk)
                    else:
                        row.update(item, self.to_datetime(item.created_at))
            else:
                """ 업데이트 모드가 아니면, 데이터를 추가만 함.
                    id list들에 있는 UserDetail을 rows에 불러온 뒤, rows안에 있으면
                    추가하지 않음.
                """ 
                rows = sess.query(UserDetail).filter(UserDetail.id.in_(self.userdetaillist_to_idlist(user_list))).all()
                for item in user_list:
                    if self.id_in(item.id, rows):
                        continue
                    user_chunk = UserDetail(item, self.to_datetime(item.created_at))
                    print "Added %d" % ( item.id )
                    sess.add(user_chunk)
            sess.commit()

            sess.close()
            return True

        except TwitterError as e:
            t = TweetErrorHandler(e)
            t.add_handler(ErrorNumbers.RATE_LIMIT_ERROR, self.rate_limit_handler)
            result = t.invoke(process_name=self.process_name)
            if sess is not None:
                sess.commit()
                sess.close()
            return result

    @Crawler.user_list_info
    def get(self, listof_user_id, **kwargs):
        try:
            ts = TweetSupport()
            api = ts.get_api()
            user_list = api.UsersLookup(
                    user_id=listof_user_id,
                    include_entities=kwargs['include_entities'] if 'include_entities' in kwargs else None)
            user_detail_list = list()
            for item in user_list:
                user_detail_list.append(UserDetail(item, self.to_datetime(item.created_at)))
            return user_detail_list
        except TwitterError as e:
            t = TweetErrorHandler(e)
            t.add_handler(ErrorNumbers.RATE_LIMIT_ERROR, self.rate_limit_handler)
            result = t.invoke(process_name=self.process_name)
            return result

    def userdetaillist_to_idlist(self, userdetail_list):
        result = list()
        for item in userdetail_list:
            result.append(item.id)
        return result

    def id_in(self, id, rows):
        for item in rows:
            if item.id == id:
                return True
        return False

if __name__ == "__main__":
    u = UserLookupCrawler()
#    u.crawling(listof_user_id=[20, 2263011, 5607572])
