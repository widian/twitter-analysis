#!/usr/bin/env python
# -*- coding:utf8 -*-

collections = ['cindemas']

cinde_characters = [u"시부야 린", u"혼다 미오", u"시마무라 우즈키", u"후타바 안즈", u"타카가키 카에데", u"죠가사키 리카", u"미무라 카나코", u"칸자키 란코", u"모로보시 키라리", u"마에카와 미쿠", u"타다 리아나", u"죠가사키 미카", u"코히나타 미호", u"카와시마 미즈키", u"토토키 아이리", u"아베 나나", u"닛타 미나미", u"히노 아카네", u"코시미즈 사치코", u"시라사카 코우메", u"아카기 미리아", u"사쿠마 마유", u"아나스타샤", u"타카모리 아이코", u"오가타 치에리", u"카미야 나오", u"호시 쇼코", u"코바야카와 사에", u"호죠 카렌", u"호리 유코", u"미야모토 프레데리카", u"사가사와 후미카", u"히메카와 유키", u"이치노세 시키", u"하야미 카나데", u"이치하라 니나", u"사쿠라이 모모카", u"타치바나 아리스", u"카타기리 사나에", u"시오미 슈코", u"아이바 유미", u"무카이 타쿠미"]
storage = list()
storage.append(cinde_characters)
def get_character(collection_number, character_number):
    if collection_number >= len(collections):
        return False
    character_list = storage[collection_number]
    if character_number >= len(character_list):
        return False
    return character_list[character_number]

def get_collection(collection_number):
    return collections[collection_number]

if __name__ == "__main__":
    print get_character(0, 1)
    print get_character(1, 0)
    print get_character(0, 45)
    print get_collection(0)
