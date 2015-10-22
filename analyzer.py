#!/usr/bin/env python
# -*- coding:utf8 -*-

from __future__ import print_function

from support.mysql_support import Session
from support.model import Tweet
from collections import OrderedDict

# NLP Processors
from twkorean import TwitterKoreanProcessor

def analyze():
    sess = Session()
    ps = PrintString()
    processor = TwitterKoreanProcessor(stemming=False)

    tweets = sess.query(Tweet)\
                 .filter(Tweet.user == 444465942) \
                 .all()
    noun_usage_dict = OrderedDict()
    noun_counter = 0
    for tweet in tweets:
        tokens = processor.tokenize(tweet.text)
        for token in tokens:
            if token.pos == 'Noun':
                noun_counter += 1
                if token.text in noun_usage_dict:
                    noun_usage_dict[token.text] += 1
                else:
                    noun_usage_dict[token.text] = 1
        ps.print_tokens(tokens)
        print(noun_counter)
    for item in OrderedDict(sorted(noun_usage_dict.items(), key = lambda t:t[1], reverse=True)).items():
        print(item[0], item[1])

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
    #analyze()

    processor = TwitterKoreanProcessor(stemming=False)
    text = u"나바로가 홈런을 쳐서 삼성이 4:0으로 승리했다 쩔엌ㅋㅋㅋㅋㅋ" 
    text = u"대신증권사에서 마이다스미소중소형주증권투자신탁상품을 가입했어요"
    text = u"미등록어 처리가 강화된 복합명사 분해논문에서의 해석방식은 자연어 전처리에 큰 영향을 미쳤다"
    tokens = processor.tokenize(text)
    ps = PrintString()
    ps.print_tokens(tokens)

    