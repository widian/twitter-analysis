#!/usr/bin/env python
# -*- coding:utf8 -*-

from __future__ import print_function

from collections import OrderedDict

# NLP Processors
from twkorean import TwitterKoreanProcessor

from support.mysql_support import Session, AnalysisSession
from support.model import Tweet, User, TweetType
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

def tweet_collect(analysis_type=None):
    sess = Session()
    if analysis_type is None or not isinstance(analysis_type, AnalysisType):
        print("Unknown Analysis Type")
        return False
    tweet_type_query = analysis_type.make_query(sess)
    type_result = tweet_type_query.first()
    if type_result is not None:
        """ cached된 typed tweet이 있을 때
        """
        #TODO : 캐싱된 트윗 리스트가 최신인지 확인하고 정리해야함
        print("DEFINED TYPE")
    else:
        #TODO : Tweet Type을 추가시키고 tweet을 캐싱 한 뒤에 
        #       캐싱 된 시점을 저장해야함.
        tweet_type_data = analysis_type.make_type_data()
        sess.add(tweet_type_data)
        sess.commit()
        type_result = tweet_type_query.first()


        #Type의 번호를 type_result로부터 얻을 수 있음.

    sess.close()
    return True

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
        self.contain_retweet = contain_retweet
        self.contain_linked_tweet = contain_linked_tweet
        self.contain_username_mentioned = contain_username_mentioned
        self.contain_english = contain_english
        self.least_tweet_per_user = least_tweet_per_user
        self.since = since
        self.until = until
        self.follower_of = follower_of

    def get_tweet_list(self, target_tweet_table, session):
        #TODO : FILL IT!
        query = session.query(target_tweet_table)
        if self.since is not None:
            query = query.filter(target_tweet_table.created_at > self.since)
        if self.until is not None:
            query = query.filter(target_tweet_table.created_at < self.until)
        if self.contain_retweet == 0:
            query = query.filter(target_tweet_table.retweet_owner == None)
        elif self.contain_retweet == 2:
            query = query.filter(target_tweet_table.retweet_owner != None)
        if self.contain_username_mentioned == 0:
            query = query.filter(target_tweet_table.reply_to == None)
        elif self.contain_username_mentioned == 2:
            query = query.filter(target_tweet_table.reply_to != None)
        pre_tweets = query.all()
        return pre_tweets

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
#    noun_usage_result = analyze(9040962)

#    processor = TwitterKoreanProcessor(stemming=False)
#    text = u"나바로가 홈런을 쳐서 삼성이 4:0으로 승리했다 쩔엌ㅋㅋㅋㅋㅋ" 
#    text = u"대신증권사에서 마이다스미소중소형주증권투자신탁상품을 가입했어요"
#    text = u"미등록어 처리가 강화된 복합명사 분해논문에서의 해석방식은 자연어 전처리에 큰 영향을 미쳤다"
#    tokens = processor.tokenize(text)
#    ps = PrintString()
#    ps.print_tokens(tokens)
#
#    user_analyze()
#
#    korean_analyze(14206146)

#    tweet_collect(AnalysisType( since=datetime.date(2015, 10, 1), 
#                      until=datetime.date(2015, 10, 10), 
#                      follower_of=335204566,
#                      contain_retweet=0,
#                      contain_english=0,
#                      contain_username_mentioned=0,
#                      contain_linked_tweet=0,
#                      least_tweet_per_user=200)
#                 )
    from support.model import Tweet_335204566_1
    sess = Session()
    tweets = AnalysisType( since=datetime.date(2010, 10, 1), 
                      until=datetime.date(2010, 10, 10), 
                      follower_of=335204566,
                      contain_retweet=0,
                      contain_english=0,
                      contain_username_mentioned=0,
                      contain_linked_tweet=0,
                      least_tweet_per_user=200).get_tweet_list(Tweet_335204566_1, sess)
    for tweet in tweets:
        print(tweet.text)
    print(len(tweets))
    sess.close()
    
                 


