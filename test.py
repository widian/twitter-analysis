a = u'\ub0b4\ubabd\uace0\uc790\uce58\uad6c\uc758 \ud589\uc815\uad6c\uc5ed\uba85\uc740 \uc911\uad6d \ubcf8\ud1a0\uc758 \uac83\uacfc \ub2e4\ub978\ub370, \ud604\u7e23\uc740 \ub9f9\u76df, \ud5a5\u9115\uc740 \uae30\U00023103. \uccad\ub300 \ubabd\uace0\uc871\uc758 \ud1b5\uce58 \ub2e8\uc704\uc5d0\uc11c \uc5f0\uc6d0.'

print a

import analyzer
from twkorean import TwitterKoreanProcessor

ps = analyzer.PrintString()

processor = TwitterKoreanProcessor(stemming=False)

tokens = processor.tokenize(a)

#ps.print_tokens(tokens)

test_link = "asdfasdf asdfzxc http://t.co/aasdfasdf"
import re
myre = re.compile(r'http[s]?:\/\/.*[\r\n]*')
test = myre.sub('http://t.co/???', test_link)
print test
