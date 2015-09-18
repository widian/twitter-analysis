#!/usr/bin/env python
# -*- coding:utf8 -*-

collections = ['cindemas']

cinde_characters = ["시부야 린", "혼다 미오", "시마무라 우즈키", "후타바 안즈", "타카가키 카에데", "죠가사키 리카", "미무라 카나코", "칸자키 란코", "모로보시 키라리", "마에카와 미쿠", "타다 리아나", "죠가사키 미카", "코히나타 미호", "카와시마 미즈키", "토토키 아이리", "아베 나나", "닛타 미나미", "히노 아카네", "코시미즈 사치코", "시라사카 코우메", "아카기 미리아", "사쿠마 마유", "아나스타샤", "타카모리 아이코", "오가타 치에리", "카미야 나오", "호시 쇼코", "코바야카와 사에", "호죠 카렌", "호리 유코", "미야모토 프레데리카", "사가사와 후미카", "히메카와 유키", "이치노세 시키", "하야미 카나데", "이치하라 니나", "사쿠라이 모모카", "타치바나 아리스", "카타기리 사나에", "시오미 슈코", "아이바 유미", "무카이 타쿠미"]
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
