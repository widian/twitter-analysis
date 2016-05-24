#!/usr/bin/env python
# -*- coding:utf8 -*-

#TODO : Apriori Algorithm 구현
class AprioriSupport(object):

    initial_candidate_set = None

    def __init__(self):
        self.initial_candidate_set = dict()

    def count_itemset(self, itemset, target):
        count = 0
        for item in itemset:
            if item == target:
                count += 1
        return count

    def gen_candidate_set(self, itemset, min_sup_value):
        pass

    def add(self, item):
        key = item.make_key()
        if key in self.initial_candidate_set:
            self.initial_candidate_set[key] += 1
        else:
            self.initial_candidate_set[key] = 1

    def prune(self, candidate_set, min_sup_value):
        new_candidate_set = dict()
        for key, value in candidate_set.iteritems():
            if value < min_sup_value:
                continue
            else:
                new_candidate_set[key] = value
        return new_candidate_set

    def candidate_generate(self, candidate_set, min_sup_value):
        new_condidate_set = dict()

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

        if self.has_next and comparer.has_next():
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

    def add_next(self, next_item):
        self.next_item = next_item

    def make_key(self):
        key = "{0}{1}".format(self.pos, self.length)
        return key

    def __repr__(self):
        return self.make_key()

if __name__ == '__main__':
    pass
