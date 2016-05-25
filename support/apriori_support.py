#!/usr/bin/env python
# -*- coding:utf8 -*-

class AprioriSupport(object):
    initial_candidate_set = None

    def __init__(self):
        self.initial_candidate_set = dict()

    def add(self, item):
        key = item.make_key()
        if key in self.initial_candidate_set:
            self.initial_candidate_set[key].add()
        else:
            self.initial_candidate_set[key] = ItemValue(item)

    def prune(self, candidate_set, min_sup_value):
        new_candidate_set = dict()
        for key, item in candidate_set.iteritems():
            if item.value < min_sup_value:
                continue
            else:
                new_candidate_set[key] = item
        return new_candidate_set

    def itemset_generate(self, candidate_set):
        itemset = set([])
        iter_candidate_set = candidate_set.copy()
        for key, value in candidate_set.iteritems():
            del(iter_candidate_set[key])
            for key2, value2 in iter_candidate_set.iteritems():
                if value.item.concatable(value2.item):
                    itemset.add(value.item.concat(value2.item))
        return itemset

    def candidate_generate(self, itemset, min_sup_value):
        for key, value in candidate_set.iteritems():
            print key, value

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

class AnalyzeItem(object):
    length = 0
    pos = None

    next_item = None

    def __init__(self, length, pos):
        self.length = length
        self.pos = pos

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
        a = AnalyzeItem(self.length, self.pos)
        a.next_item = item.clone()
        return a

    def add_next(self, next_item):
        self.next_item = next_item

    def make_key(self):
        key = "{0}{1}".format(self.pos, self.length)
        if self.has_next():
            key = "{0}{1}".format(key, self.next_item.make_key())
        return key

    def compare_item(self, item):
        key1 = "{0}{1}".format(self.pos, self.length)
        key2 = "{0}{1}".format(item.pos, item.length)
        return key1 == key2

    def clone(self):
        a = AnalyzeItem(self.length, self.pos)
        if self.has_next():
            a.add_next(self.next_item.clone())
        return a
        
    def __repr__(self):
        return self.make_key()

if __name__ == '__main__':
    a = AnalyzeItem(1, 'a')
    b = AnalyzeItem(3, 'asd')
    c = AnalyzeItem(2, 'dss')
    h = AnalyzeItem(1, 'c')

    d = AnalyzeItem(3, 'asd')
    e = AnalyzeItem(2, 'dss')
    g = AnalyzeItem(1, 'c')
    f = AnalyzeItem(1, 'b')

    i = AnalyzeItem(5, 'k')

    a.add_next(b)
    b.add_next(c)
    c.add_next(h)

    d.add_next(e)
    e.add_next(i)
    i.add_next(f)
    print a.concatable(d), a.clone(), a, a.is_same(a.clone())

    a2 = AnalyzeItem(1,'a')
    b2 = AnalyzeItem(2,'b')
    print a2.concatable(b2)
