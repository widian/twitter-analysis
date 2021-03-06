#!/usr/bin/env python
# -*- coding:utf8 -*-

from __future__ import print_function

from collections import OrderedDict

# NLP Processors
from twkorean import TwitterKoreanProcessor

from support.mysql_support import Session, AnalysisSession
from support.model import Tweet, User, TweetType, TweetSearchLog, Relationship, WordTable, WordAnalysisLog, UserList, WordAnalysisLogWithoutBot, UserListType
from sqlalchemy import desc, func

from support.analyzer_model import Word, AnalysisType, PrintString
from support.apriori_support import AnalyzeItem, AprioriSupport

import datetime

def user_analyze():
    sess = Session()
    ps = PrintString()

    processor = TwitterKoreanProcessor()

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

def tweet_reduce_dict(analysis_type, table_list):
    table_list.reverse()
    sess = Session()
    if analysis_type is None or not isinstance(analysis_type, AnalysisType):
        print("Unknown Analysis Type")
        return False
    tweet_type_query = analysis_type.make_query(sess)
    type_result = tweet_type_query.first()
    tweets = dict()
    for table in table_list:
        result = analysis_type.get_tweet_userdict(table, sess)
        if result is not None:
            for key, value in result.iteritems():
                if key in tweets:
                    tweets[key] = tweets[key] + value
                else:
                    tweets[key] = value
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
        #TODO : TweetType에 트윗 검색이 캐시된 시간을 저장해놓는 용도를 추가
        #       트윗을 재검색할 수 있도록?
        """ 혹시 있을지 모르는 트윗 검색 캐시를 제거
        """
        sess.query(TweetSearchLog).filter(TweetSearchLog.tweet_type == type_id)\
                                  .delete(synchronize_session='evaluate')
        for user, tweet_list in tweets.iteritems():
            """ tweets : key - user, value - list of tweets
            """
            for tweet in tweet_list:
                tweet_search_log = TweetSearchLog(tweet.id, type_id)
                sess.add(tweet_search_log)
        sess.commit()
    sess.close()
    return tweets


def tweet_reduce(analysis_type, table_list):
    table_list.reverse()
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

        #TODO : TweetType에 트윗 검색이 캐시된 시간을 저장해놓는 용도를 추가
        #       트윗을 재검색할 수 있도록?
        """ 혹시 있을지 모르는 트윗 검색 캐시를 제거
        """
        sess.query(TweetSearchLog).filter(TweetSearchLog.tweet_type == type_id)\
                                  .delete(synchronize_session='evaluate')
        for tweet in tweets:
            tweet_search_log = TweetSearchLog(tweet.id, type_id)
            sess.add(tweet_search_log)
        sess.commit()
    sess.close()
    return tweets

def get_userset_from_tweetlist(tweet_list):
    user_set = set([])
    for tweet in tweet_list:
        user_set.add(tweet.user)
    return user_set

def analysis_tweets_without_bot(analysis_type, tweet_list, bot_list):
    sess = Session()
    processor = TwitterKoreanProcessor()
    word_dict = dict()
    word_count_dict = dict()
    temp_count = 0
    for tweet in tweet_list:
        if tweet.user in bot_list:
            continue
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
            temp_count += 1
            if temp_count % 5000 == 0:
                print("{0} words counted".format(temp_count))
    tweet_type_data = analysis_type.make_query(sess).first()
    print("Word Cound Dict generated")
    if tweet_type_data is None:
        raise Exception('We need tweet search log type')

    #NOTE : DELETE
    sess.query(WordAnalysisLogWithoutBot).filter(WordAnalysisLogWithoutBot.search_log_type == tweet_type_data.id)\
                               .delete(synchronize_session='evaluate')
    count = 0
    for key, value in word_count_dict.iteritems():
        sess.add(WordAnalysisLogWithoutBot(key, value, tweet_type_data.id))
        count += value
    sess.commit()
    sess.close()
    return count


def analysis_tweets(analysis_type, tweet_list):
    sess = Session()
    processor = TwitterKoreanProcessor()
    word_dict = dict()
    word_count_dict = dict()
    temp_count = 0
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
            temp_count += 1
            if temp_count % 5000 == 0:
                print("{0} words counted".format(temp_count))
    tweet_type_data = analysis_type.make_query(sess).first()
    print("Word Cound Dict generated")
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

def produce_analysis_type(type_number):
    sess = Session()
    analysis_type_result = sess.query(TweetType).filter(TweetType.id == type_number).first()

    analysis_type = AnalysisType(since=analysis_type_result.since,
                                 until=analysis_type_result.until,
                                 count=analysis_type_result.count,
                                 use_processor=True if analysis_type_result.use_processor == 1 else False,
                                 follower_of=analysis_type_result.follower_of,
                                 contain_linked_tweet=analysis_type_result.contain_linked_tweet,
                                 contain_username_mentioned=analysis_type_result.contain_username_mentioned,
                                 contain_english=analysis_type_result.contain_english,
                                 contain_retweet=analysis_type_result.contain_retweet,
                                 least_tweet_per_user=analysis_type_result.least_tweet_per_user,
                                 user_list_type=analysis_type_result.user_list_type)
    return analysis_type

def export_result_to_csv(tweet_type):
    sess = Session()
    items = sess.query(WordAnalysisLog).filter(WordAnalysisLog.search_log_type == tweet_type)\
                                       .order_by(desc(WordAnalysisLog.word_count))\
                                       .all()
    f = open(".././data/%03d_analysis.csv" % tweet_type, 'w')
    f.write('word, pos, is_unknown, count\n')
    for item in items:
        text = "%s, %s, %d, %s\n" % (item.word.word, item.word.pos, item.word.unknown, item.word_count)
        f.write(text)
    f.close()
    sess.close()

class TextPos(object):
    text = None
    order_of_pos = list()

    def __init__(self, text=None, order_of_pos=list()):
        self.text = text
        self.order_of_pos = order_of_pos

class SentenceAnalysis(object):

    def get_tweet_list(self, target_tweet_table, tweet_type, session):
        query = session.query(target_tweet_table)
        subquery_search_log = session.query(TweetSearchLog.tweet_id).filter(TweetSearchLog.tweet_type == tweet_type).subquery()
        query = query.filter(target_tweet_table.id.in_(subquery_search_log))
        return query.all()

    def cosine_sentence_similarity(self):
        """ http://stackoverflow.com/questions/15173225/how-to-calculate-cosine-similarity-given-2-sentence-strings-python
            cosine similarity with pure python
        """ 
        import re, math
        from collections import Counter

        processor = TwitterKoreanProcessor()

        def get_cosine(vec1, vec2):
             intersection = set(vec1.keys()) & set(vec2.keys())
             numerator = sum([vec1[x] * vec2[x] for x in intersection])

             sum1 = sum([vec1[x]**2 for x in vec1.keys()])
             sum2 = sum([vec2[x]**2 for x in vec2.keys()])
             denominator = math.sqrt(sum1) * math.sqrt(sum2)

             if not denominator:
                return 0.0
             else:
                return float(numerator) / denominator

        def text_to_vector(text):
            words = processor.tokenize_to_strings(text)
            return Counter(words)
        text1 = "#오션파라다이스주소 주소 PKK558,COM  르 돈 승 상 팅 며 진 운 액 진 넘 본 천 어 정 때 낮 은 있 무 장 총 회 직 보 양 라쿠텐 아 크루즈 급 솔레어카지노 바"
        text2 = "#릴게임바다 주소 W W W , S S H 9 9 6, C O M  세 아 법 카 블 게 입 요 분 쪽 올 뾻 임 팅 양 액 며 광 업 것 러 심 돈 스 띄 망 미소 업 카지노게임설명 븐 소프 입"

        vector1 = text_to_vector(text1)
        vector2 = text_to_vector(text2)

        cosine = get_cosine(vector1, vector2)

        print( 'Cosine:', cosine )

def count_tweet(source_tablelist, user_id):
    sess = Session()
    count = list()
    for table in source_tablelist:
        result = sess.query(table).filter(table.user == user_id).all()
        #print("{0} tweets in {1}".format(len(result), table.__tablename__))
        for tweet in result:
            if tweet.id in count:
                continue
            else:
                count.append(tweet.id)
    sess.close()
    count.sort(reverse=True)
    print("counted {0}".format(user_id))
    return count

def add_userlist():
    detected_spam_list = []
    detected_user_list = []
    common_user_list = []
    not_detected_bot_list = []
    from support.model import Tweet_test_dataset

    def add_tweet_to_table(source_tablelist, target_table, counter, user_id, type_id):
        sess = Session()
        id_list = list()
        for table in source_tablelist:
            tweet_list = sess.query(table).filter(table.user == user_id).all()
            for tweet in tweet_list:
                if tweet.id in id_list:
                    continue
                else:
                    if tweet.id in counter[:200]:
                        sess.add(Tweet_test_dataset(tweet, type_id))
                        id_list.append(tweet.id)
            sess.commit()
        sess.close()


    def tool(user_list, type_id):
        from support.model import Tweets
        detected_user_set = set([])
        user_tweet_dict = dict()
        for item in user_list:
            if item in detected_user_set:
                continue
            else:
                counter = count_tweet(Tweets, item)
                if  len(counter) >= 200:
                    user_tweet_dict[item] = counter
                    detected_user_set.add(item)
        count = 0
        for user in detected_user_set:
            if count > 100:
                break
            else:
                add_tweet_to_table(Tweets, Tweet_test_dataset, user_tweet_dict[user], user, type_id)
                count += 1
    
    #tool([item for item in detected_user_list if item not in detected_spam_list], 2)
    tool([item for item in not_detected_bot_list if item not in detected_spam_list and item not in detected_user_list], 3)
    #tool(common_user_list, 4)


def get_tweetlist_based_on_userlist(userlist_type, tweet_type):
    """ 특정 analysis type의 조건에 맞는 트윗 중 subquery_userlist안에 있는 유저들의 트윗만 선별적으로 추출합니다
    """
    sess = Session()
    from support.model import Tweets
    from sqlalchemy import and_

    # DEBUG : TEST LIST
    user_list = [328207123,
        387754652,
        459058358,
        2827044096,
        2884600289,
        2996035123,
        3834891792
        ]
    subquery_userlist = sess.query(UserList.user_id).filter(UserList.list_type == userlist_type).subquery()
    for tweetset in Tweets:
        for table in tweetset:
            filter_item = list()
            filter_item.append(table.user.in_(subquery_userlist))
            tweets = produce_analysis_type(tweet_type).add_filter_to_query(table, sess.query(table)).filter(and_(*filter_item) if len(filter_item) > 1 else filter_item[0]).group_by(table.user).all()
            #TODO : TODO using tweets
            for item in tweets:
                print(item.user)
    sess.close()  


def apriori_item_search(tweet_list, min_sup_value):
    """ apriori item으로 tokens를 frequent depend search.
        apriori에 들어오는 tweet_list는 유저별 tweet_list여야함
    """
    apriori_support = AprioriSupport()
    processor = TwitterKoreanProcessor(normalization=False, stemming=False)
    list_of_tokens = list()
    for tweet in tweet_list:
        tokens = processor.tokenize(tweet.text)
        list_of_tokens.append(tokens)

    for tokens in list_of_tokens:
        for item in tokens:
            candidate = AnalyzeItem(len(item.text), item.pos, text=item.text)
            apriori_support.add(candidate)
    apriori_support.prune(min_sup_value)
    print( "item_set after prune : " , apriori_support.item_set )
    for tokens in list_of_tokens:
        for item in tokens:
            candidate = AnalyzeItem(len(item.text), item.pos)
            apriori_support.map_new_itemset(candidate)

    print( "candidate_set after map_new_itemset : ", apriori_support.candidate_set )
    print( "item_set after map_new_itemset: ", apriori_support.item_set )
    apriori_support.reset_apriori_variables()
    apriori_support.move_itemset()
    print( "item_set after move_itemset : ", apriori_support.item_set )

    while len(apriori_support.item_set) != 0:
        apriori_support.reset_apriori_variables()
        for tokens in list_of_tokens:
            for token in tokens:
                item = AnalyzeItem(len(token.text), token.pos, text=token.text)
                apriori_support.search_add(item)
        print ("candidate_set after search_add : ", apriori_support.candidate_set)
        apriori_support.prune(min_sup_value)
        print ("candidate_set after prune : ", apriori_support.candidate_set)
        apriori_support.itemset_generate()
        print("item_set after prune : " ,apriori_support.item_set)
    print("candidate_set after apriori : " , apriori_support.candidate_set )
    return apriori_support.candidate_set

if __name__ == '__main__':
#
#    korean_analyze(14206146)
#   export_result_to_csv(6) 

    def get_tweetlist_based_on_tweet_search_log():
        from support.model import Tweet_335204566_9
        sess = Session()
        se = SentenceAnalysis()
        result = se.get_tweet_list(Tweet_335204566_9, 18, sess)
        for item in result:
            print(item.text)
        sess.close()

    def similarity_test():
        se = SentenceAnalysis()
        se.cosine_sentence_similarity()
    def apriory_similarity_test():
        """ apriori property를 이용한 두 text의 유사성검사.
            위의 pos기반 similarity 비교에 대한 대응군.
        """

        text = "#오션파라다이스주소 주소 PKK558,COM  르 돈 승 상 팅 며 진 운 액 진 넘 본 천 어 정 때 낮 은 있 무 장 총 회 직 보 양 라쿠텐 아 크루즈 급 솔레어카지노 바"
        text2 = "#릴게임바다 주소 W W W , S S H 9 9 6, C O M  세 아 법 카 블 게 입 요 분 쪽 올 뾻 임 팅 양 액 며 광 업 것 러 심 돈 스 띄 망 미소 업 카지노게임설명 븐 소프 입"

        processor = TwitterKoreanProcessor(normalization=False, stemming=False)
        tokens = processor.tokenize(text)
        tokens2 = processor.tokenize(text2)

        apriori_item_search(tokens, 3)


    def analysis_test():
        """ TwitterKoreanProcessor의 동작 테스트
        """
        text = "#오션파라다이스주소 주소 PKK558,COM  르 돈 승 상 팅 며 진 운 액 진 넘 본 천 어 정 때 낮 은 있 무 장 총 회 직 보 양 라쿠텐 아 크루즈 급 솔레어카지노 바"

        processor = TwitterKoreanProcessor(normalization=False, stemming=False)
        tokens = processor.tokenize(text)
        p = PrintString()
        p.print_tokens_plain(tokens)

#    apriory_similarity_test()
#    analysis_test()
#    get_tweetlist_based_on_tweet_search_log()
#    pos_similarity_analyze()
#    similarity_test()
