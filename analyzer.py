#!/usr/bin/env python
# -*- coding:utf8 -*-

from __future__ import print_function

from collections import OrderedDict

# NLP Processors
from twkorean import TwitterKoreanProcessor

from support.mysql_support import Session, AnalysisSession
from support.model import Tweet, User, TweetType, TweetSearchLog, Relationship, WordTable, WordAnalysisLog, UserList, WordAnalysisLogWithoutBot
from sqlalchemy import desc, func

from support.analyzer_model import Word, AnalysisType, PrintString, UserListType
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

def add_tweet_to_table(source_tablelist, target_table, user_id):
    sess = Session()
    id_list = set([])
    for table in source_tablelist:
        tweet_list = sess.query(table).filter(table.user == user_id).all()
        for tweet in tweet_list:
            if tweet.id in id_list:
                continue
            else:
                sess.add(tweet)
                id_list.add(tweet.id)
        sess.commit()
    sess.close()

def count_tweet(source_tablelist, user_id):
    sess = Session()
    count = 0
    for table in source_tablelist:
        result = sess.query(func.count(table.id)).filter(table.user == user_id).first()[0]
        print("{0} tweets in {1}".format(result, table.__tablename__))
        count += result
    sess.close()
    return count

def add_userlist():
    detected_spam_list = [
            4178359274,4288394478,4506144794,4742754421,4858531693,697240444539777024,697249016120107008,23553828,112929553,149528889,213591116,242208170,2583593708,3093756931,3243036565,3318457591,3321044234,3812303712,3824056873,4178359274,4288394478,4506144794,4742754421,4858531693,697240444539777024,697249016120107008,705334495864434688,706073886027182080,707260375352250369,707280829244788736,707281391948419072,707281979541049344,707282553154048000,707289052077133824,707291528503242753,707502775760867328,707653057643827200,707655168192479232,711852949169766401,714380458474078208,715924858689818624,65672367,137391554,141813142,150188841,206599758,213591116,220917609,232095372,243534030,249634438,330831751,396493096,423249134,454640965,499593695,716347784,897638604,1178503771,1350405198,1398527784,1477010395,1707765817,1859902014,2365448508,2432786514,2498770772,2556129524,2583593708,2680594423,2760038280,2794081040,2794095324,2840204916,2846682182,2849003210,2899254996,2919496194,2944971055,2951061259,2963375767,3182358433,3188677128,3230627290,3231813578,3244356463,3288491149,3303524533,3656393113,3657273618,3824056873,4057211904,4178359274,4288394478,4506144794,4723359678,4742044717,4742754421,4807663003,4855060994,4858531693,4862553193,36270446,44532588,48661131,65672367,79958736,84191757,87172091,102659815,104088658,107899938,114959393,123102247,129740742,133630519]
    detected_user_list = [
            4316019677,14205016,35260767,48661131,56057829,64358254,79958736,134737741,254265179,395289386,435990930,488425281,2282209052,3123415830,4316019677,35766346,89133606,102659815,109878560,114959393,131803555,133997178,134737741,135206134,135790315,144305501,148244142,152182156,161725422,184729579,187299087,187456709,194472875,194605222,212614576,223429138,232390465,295543910,307389351,315575130,318330451,352077570,355162705,403981054,433026789,539100499,541418168,884302249,1306856424,1321705800,1342378729,1399019070,1476431246,1696884560,1916249556,2282209052,2297866105,2341836942,2445293076,2700893606,2850445802,3020298709,3068166596,3092341636,3123415830,4224144026,4470129559,4668186733,12518132,14205016,41509817,55446640,56057829,56310613,56626319,74442459,75053379,94758818,97843248,107892938,112929553,125521090,132167437,134737741,135135949,144305501,148244142,152182156,152864656,156237461,157933161,161725422,161759760,162910077,165498778,166094321,171837374,180204565,184099205,184729579,194605222,196194047,215489441,223429138,223509630,226632657,232688037,239396890,243982484,245221589,246192895,246291090,250488224,250691219]
    common_user_list = [
            49314267,3176154216,1349708664,3456717560,4565768534,4538384838,1476973309,4713926280,1474300824,1693269036,1720378316,3273039740,4648134619,3145542212,630898393,3598901594,4585799412,3176154216,3845440332,3300473294,3320472913,3494160920,3689733612,3404430679,3119927382,360075611,4021989912,3669385873,710320046,418447111,1454513514,573377616,3275099154,746772601,230464665,4591090033,310163008,3281787248,917939978,824812658,743697690,3118374245,3231311670,3315255450,3274245624,782287592,3992252652,4101124214,1610754289,3415073353,580935323,1625804250,1037384426,4378875919,784777862,1287447648,793884452,427435701,1145099924,3233386554,3290692159,3835646233,414017209,1625727733,522066001,795207906,1067744514,3101662274,3309745447,483884207,1530880122,3124300801,1646481822,4442900954,1217192096,513022574,734935302,4725282798,540057532,1554486092,3978899832,381517141,1291184970,1037365122,4835226630,3241721970,1649906220,4294765933,3338114540,421816506,4740730512,546851638,1049411870,3999906793,3045459667,357899607,1050598536,4279798158,3517346358,561827078,4682913012]
    not_detected_bot_list = [
            570769089,868838005,1012931922,1742900155,2257809955,3314708328,3320991570,3884048240,3971143392,4020101714,4241241613,4332357972,4481379074,4484452998,4497868099,150188841,212853729,234984645,329061975,353003786,373362754,407348890,422322630,462745325,566837708,586650942,620873095,625509620,878221171,984731942,1006403702,1012931922,1032402841,1050540708,1078420494,1194011839,1255702842,1331486280,1553901756,1572888872,1584812912,1859902014,2154424592,2831666142,2943964182,2961837198,3161549569,3311180395,3503471960,3670599672,3701184614,3702850279,3873191713,3940628414,4078718772,4088140152,4131266473,4151642952,4152348072,4178359274,4230169280,4241241613,4253032813,4288394478,4310636773,4318524673,4321085592,4324959917,4329446172,4332357972,4340587693,4559479579,4561975394,4564727718,4565433553,4592142132,4599392966,4608928226,4617770358,4623852692,4642224456,4644437053,4645196293,4647695172,4649211684,4662354673,4666023254,4670189654,4677385873,4741060224,4746747025,4756564868,4758421158,4788589219,4788990192,4793528904,4793641814,4797841700,4800765432,4803393248,4849551013,695037236287385601,697240444539777024]

    detected_user_set = set([])
    for item in not_detected_bot_list:
        detected_user_set.add(item)
    print(len(detected_user_set))

add_userlist()


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

    from support.model import Tweets
    print(count_tweet(Tweets, 112929553))
#    apriory_similarity_test()
#    analysis_test()
#    get_tweetlist_based_on_tweet_search_log()
#    pos_similarity_analyze()
#    similarity_test()
