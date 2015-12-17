#!/usr/bin/env python
# -*- coding:utf8 -*-

from __future__ import print_function

from collections import OrderedDict

# NLP Processors
from twkorean import TwitterKoreanProcessor

from support.mysql_support import Session, AnalysisSession
from support.model import Tweet, User, TweetType, TweetSearchLog, Relationship, WordTable, WordAnalysisLog
from sqlalchemy import desc


def analyze(user_id):
    sess = Session()
    ps = PrintString()
    processor = TwitterKoreanProcessor(stemming=False)

    tweets = sess.query(Tweet)\
                 .filter(Tweet.user == user_id) \
                 .all()
    noun_usage_dict = OrderedDict()
    noun_counter = 0
    tweet_tokens = list()
    for tweet in tweets:
        tokens = processor.tokenize(tweet.text)
        tweet_tokens.append(tokens)
        for token in tokens:
            print(token.unknown)
            if token.pos == 'Noun':
                noun_counter += 1
                if token.text in noun_usage_dict:
                    noun_usage_dict[token.text] += 1
                else:
                    noun_usage_dict[token.text] = 1
        print(tweet.text)
        ps.print_tokens(tokens)
#        print(noun_counter)
    sess.close()
    return noun_usage_dict, noun_counter, tweet_tokens

def user_analyze():
    sess = Session()
    ps = PrintString()

    processor = TwitterKoreanProcessor(stemming=False)

    users = sess.query(User)\
                .filter(User.language_type == None)\
                .filter(User.tweet_collected_date != None)\
                .all()

    for user in users:
        user_id = user.id
        noun_usage_dict = OrderedDict()
        pos_set = set([])
        tweet_counter = 0
        tweets = sess.query(Tweet)\
                 .filter(Tweet.user == user_id)\
                 .order_by(desc(Tweet.id))\
                 .limit(200)\
                 .all()

        for tweet in tweets:
            tweet_counter += 1
            tokens = processor.tokenize(tweet.text)
            for token in tokens:
                pos_set.add(token.pos)
                if token.pos == 'Noun':
                    if token.text in noun_usage_dict:
                        noun_usage_dict[token.text] += 1
                    else:
                        noun_usage_dict[token.text] = 1
        if len(tweets) < 200:
            print(("%d is Unknown User. Tweet Count : %d") % (user_id, len(tweets)))
            user.language_type = -1
        else:
            if 'Noun' not in pos_set:
                print(("%d is Foreigner User") % user_id)
                user.language_type = 0
            else:
                print(("%d is Korean User") % user_id)
                user.language_type = 1
        #print(tweet_counter, pos_set)
        sess.commit()
    sess.close()
    return True

def korean_analyze(user_id):
    import matplotlib.pyplot as plt
    noun_usage_result = analyze(user_id)
    noun_usage_dict = noun_usage_result[0]
    noun_count = noun_usage_result[1]
    x = list()
    y = list()
    count = 0
    for item in OrderedDict(sorted(noun_usage_dict.items(), key = lambda t:t[1], reverse=True)).items():
        count += 1
        x.append(count)
        y.append(item[1])
        print(item[0], item[1], "ratio : ", item[1] / float(noun_count))

    def shows(x):
        return '$%d횟수' % (x)
    fig, ax = plt.subplots()
    ax.fmt_ydata = shows
    plt.plot(x, y, 'o')
    plt.show()

def tweet_reduce(analysis_type, table_list):
    sess = Session()
    if analysis_type is None or not isinstance(analysis_type, AnalysisType):
        print("Unknown Analysis Type")
        return False
    tweet_type_query = analysis_type.make_query(sess)
    type_result = tweet_type_query.first()
    tweets = list()
    for table in table_list:
        result = analysis_type.get_tweet_list(table, sess)
        if result is not None:
            tweets += result

    if type_result is not None:
        """ cached된 typed tweet이 있을 때
        """
        print("DEFINED TYPE")
    else:
        tweet_type_data = analysis_type.make_type_data()
        sess.add(tweet_type_data)
        sess.commit()
        type_result = tweet_type_query.first()
        type_id = type_result.id
        for tweet in tweets:
            tweet_search_log = TweetSearchLog(tweet.id, type_id)
            sess.add(tweet_search_log)
        sess.commit()
    sess.close()
    return tweets

def analysis_tweets(analysis_type, tweet_list):
    sess = Session()
    processor = TwitterKoreanProcessor(stemming=False)
    word_dict = dict()
    word_count_dict = dict()
    for tweet in tweet_list:
        tokens = processor.tokenize(tweet.text)
        for token in tokens:
            if token.pos == 'URL':
                continue
            if token.text not in word_dict:
                word_cache_query = sess.query(WordTable).filter(WordTable.word == token.text)\
                                     .filter(WordTable.pos == token.pos)
                word_cache = word_cache_query.first()
                if word_cache is None:
                    sess.add(WordTable(token.text, token.pos, token.unknown))
                    sess.commit()
                    word_cache = word_cache_query.first()
                word = Word(word_cache.word, word_cache.pos, word_cache.id)
                word_dict[token.text] = word
            word = word_dict[token.text]
            if word.id not in word_count_dict:
                word_count_dict[word.id] = 1
            else:
                word_count_dict[word.id] += 1
    tweet_type_data = analysis_type.make_query(sess).first()
    if tweet_type_data is None:
        raise Exception('We need tweet search log type')

    #NOTE : DELETE
    sess.query(WordAnalysisLog).filter(WordAnalysisLog.search_log_type == tweet_type_data.id)\
                               .delete(synchronize_session='evaluate')
    count = 0
    for key, value in word_count_dict.iteritems():
        sess.add(WordAnalysisLog(key, value, tweet_type_data.id))
        count += value
    sess.commit()
    sess.close()
    return count

def export_result_to_csv(tweet_type):
    sess = Session()
    items = sess.query(WordAnalysisLog).filter(WordAnalysisLog.search_log_type == tweet_type)\
                                       .order_by(desc(WordAnalysisLog.word_count))\
                                       .all()
    f = open("./data/%03d_analysis.csv" % tweet_type, 'w')
    f.write('word, pos, is_unknown, count\n')
    for item in items:
        text = "%s, %s, %d, %s\n" % (item.word.word, item.word.pos, item.word.unknown, item.word_count)
        f.write(text)
    f.close()
    sess.close()

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

        follower_of : follower_of의 follower인 트윗만 검색
        since : since부터의 트윗만 검색
        until : until까지의 트윗만 검색
    """
    contain_linked_tweet = 1 
    contain_english= 1
    contain_username_mentioned = 1
    contain_retweet = 1
    least_tweet_per_user = 0

    follower_of = None
    since = None
    until = None
    def __init__(self, since=None, until=None, follower_of=None, 
            contain_linked_tweet=1, contain_username_mentioned=1, contain_english=1,
            contain_retweet=1, least_tweet_per_user=0):
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

        print ('GET a user info of tweet owner from user table %s')
        tweet_count_dict = dict()
        for item in user_info:
            tweet_count_dict[item.id] = item.statuses_count

        follower_list = list()
        if self.follower_of is not None:
            follower_rows = session.query(Relationship).filter(Relationship.following == self.follower_of).all()
            for item in follower_rows:
                follower_list.append(item.follower)

        print ('GET a follower info from relationship table %s')
        processor = TwitterKoreanProcessor(stemming=False)
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
                       .filter(TweetType.least_tweet_per_user == self.least_tweet_per_user)
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
                least_tweet_per_user=self.least_tweet_per_user)


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

if __name__ == '__main__':
    import datetime
#    analyze(3146287546)
#    user_analyze()
#
#    korean_analyze(14206146)
#    export_result_to_csv(6)
    import time
    from support.model import Tweet_335204566
    analysis_type = AnalysisType( since=datetime.datetime(2015, 11, 1, 0, 0, 0), 
                      until=datetime.datetime(2015, 12, 1, 0, 0, 0), 
                      follower_of=335204566,
                      contain_retweet=2,
                      contain_english=0,
                      contain_username_mentioned=0,
                      contain_linked_tweet=0,
                      least_tweet_per_user=200)
    start = time.time()
    result = tweet_reduce( analysis_type , Tweet_335204566)
    print(time.time() - start, " for get tweet list")
    start = time.time()
    print("number of words : %d" % analysis_tweets(analysis_type, result))
    print(time.time() - start, " for analysis tweet list")
    start = time.time()
    print("number of tweets : %d" % len(result))
    sess = Session()
    export_result_to_csv(analysis_type.get_type_id(sess))
    print(time.time() - start, " for export result to csv file")
    sess.close()

    print("END")
