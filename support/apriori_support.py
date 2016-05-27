#!/usr/bin/env python
# -*- coding:utf8 -*-

class AprioriSupport(object):
    candidate_set = None
    search_block = None
    item_candidate_set = None
    item_set = None
    last_item = None
    last_candidate_set = None

    def __init__(self):
        self.candidate_set = dict()
        self.search_block = list()
        self.item_candidate_set = set([])
        self.item_set = set([])
        self.last_item = None

    def reset_apriori_variables(self):
        self.last_candidate_set = self.candidate_set
        self.search_block = list()
        self.last_item = None
        self.candidate_set = dict()

    def move_itemset(self):
        self.item_set = self.item_candidate_set

    def add(self, item):
        key = item.make_key()
        if key in self.candidate_set:
            self.candidate_set[key].add()
        else:
            self.candidate_set[key] = ItemValue(item)

    def search_add(self, item):
        """ item = AnalyzeItem
        """
        search_block = list()
#        print "item : ", item.text, item.pos, item.length
#        print "before push : ", self.search_block
        for block in self.search_block:
            """ 가지고 있는 search_block을 push함
                push하면 search_block의 다음 칸과 item을 비교하게됨
            """
            push_item = block.push()
            if push_item is None:
                """ search_block에 다음 아이템이 없으면 search_block의 원본 아이템을
                    candidate_set에 추가
                """
                self.add(block.item)
            else:
                if item.compare_item( push_item.search_target):
#                    print "after compare : ", item 
                    search_block.append( push_item )

        self.search_block = search_block
#        print "after push : ", self.search_block
        for candidate in self.item_set:
            """ candidate의 시작부분과 주어진 아이템을 비교하는 부분
            """
            if item.compare_item(candidate):
                """ 시작부분과 item이 같으면
                """
                self.search_block.append(SearchBlock(candidate))
#        print "after append : ", self.search_block

    def prune(self, min_sup_value):
        new_candidate_set = dict()
        for key, item in self.candidate_set.iteritems():
            if item.value < min_sup_value:
                continue
            else:
                new_candidate_set[key] = item
        self.candidate_set = new_candidate_set
        self.item_set = set([])
        for key, item in self.candidate_set.iteritems():
            self.item_set.add(item.item)

    def map_new_itemset(self, item):
        for val in self.item_set:
            if val.compare_item(item):
                if self.last_item is not None:
                    concat_item = self.last_item.concat(item)
                    if self.item_exist_check(concat_item, self.item_candidate_set):
                        break
                    else:
                        self.item_candidate_set.add(concat_item)
                self.last_item = item
                break

    def item_exist_check(self, target_item, target_set):
        for item in target_set:
            if target_item.is_same(item):
                return True
        return False

    def itemset_generate(self):
        itemset = set([])
        iter_candidate_set = self.candidate_set.copy()
        for key, value in self.candidate_set.iteritems():
            del(iter_candidate_set[key])
            for key2, value2 in iter_candidate_set.iteritems():
                if value.item.concatable(value2.item):
                    itemset.add(value.item.concat(value2.item))
                if value2.item.concatable(value.item):
                    concated = value2.item.concat(value.item)
                    if not self.item_exist_check(concated, self.item_set):
                        itemset.add(concated)
        self.item_set = itemset


class ItemValue(object):
    item = None
    value = 0
    def __init__(self, item):
        self.item = item
        self.value = 1
    def add(self):
        self.value += 1

    def __repr__(self):
        return "{0}".format(self.value)

class SearchBlock(object):
    key = None
    item = None
    search_target = None

    def __init__(self, item):
        self.key = item.make_key()
        self.item = item
        self.search_target = item.clone()

    def push(self):
        if self.search_target.has_next():
            self.search_target = self.search_target.next_item
            return self
        else:
            return None

    def __repr__(self):
        return "SearchBlock(item : {0}, search_target: {1})".format(self.item, self.search_target)

class AnalyzeItem(object):
    length = 0
    pos = None
    text = None

    next_item = None

    def __init__(self, length, pos, text=None):
        self.length = length
        self.pos = pos
        #NOTE : AnalyzeItem의 text는 Debug용으로 사용. Debug 종료시 text를 None으로 변경
#        self.text = text

    def is_same(self, comparer):
        """ comparer is AnalyzeItem
        """
        return_value = False
        if comparer.length == self.length and comparer.pos == self.pos:
            return_value = True
        else:
            return_value = False

        if self.has_next() and comparer.has_next():
            return return_value & self.next_item.is_same(comparer.next_item)
        elif self.has_next() and not comparer.has_next() or \
             not self.has_next() and comparer.has_next():
            return False
        else:
            return return_value
    def compare_item(self, item):
        return item.pos == self.pos and item.length == self.length
#        key1 = "{0}{1}".format(self.pos, self.length)
#        key2 = "{0}{1}".format(item.pos, item.length)
#        return key1 == key2
            
    def has_next(self):
        if self.next_item is not None:
            return True
        else:
            return False

    def len(self):
        return_value = 1
        if self.has_next():
            return return_value + self.next_item.len()
        else:
            return return_value

    def is_item_concatbale(self, target):
        return_value = False 
        for item in itemset:
            return_value = return_value | item.concatable(target)
        return return_value

    def concatable(self, item):
        """ 두개의 시퀀스 아이템이 합쳐질 수 있는 형태인지 확인하는 부분
            boolean 값을 리턴해야함. item은 뒷부분 아이템
        """
        if self.has_next():
            val = self.next_item.compare_item(item)
            if item.has_next():
                return val & self.next_item.concatable(item.next_item)
            else:
                return False
        else:
            return True


    def concat(self, item):
        """ 두개의 시퀀스 아이템을 합치는 부분
            합쳐진 아이템을 리턴해야함, item은 뒷부분 아이템
            concatable check 이후에 사용하는 편이 좋음.
        """
        a = AnalyzeItem(self.length, self.pos, text=self.text)
        a.next_item = item.clone()
        return a

    def add_next(self, next_item):
        self.next_item = next_item

    def make_key(self):
        key = "{0}{1}".format(self.pos, self.length)
        if self.has_next():
            key = "{0}{1}".format(key, self.next_item.make_key())
        return key

    def clone(self):
        a = AnalyzeItem(self.length, self.pos, text=self.text)
        if self.has_next():
            a.add_next(self.next_item.clone())
        return a
        
    def __repr__(self):
        return self.make_key()

if __name__ == '__main__':
    pass
