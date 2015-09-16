#!/usr/bin/env python
# -*- coding:utf8 -*-
import json
import flask
from flask import Blueprint, render_template

class APIResponseMaker(object):
    def make_response(self, **kwargs):
        return repr(dict(self._marshal_dict(kwargs)))

    @classmethod
    def _marshal_dict(cls, source_dict):
        for name, value in source_dict.items():
            if isinstance(value, dict):
                yield (name, dict(cls._marshal_dict(value)))
            elif isinstance(value, list):
                yield (name, list(cls._marshal_list(value)))
            elif hasattr(value, 'marshal'):
                yield (name, value.marshal())
            else:
                yield (name, value)

    @classmethod
    def _marshal_list(cls, source_list):
        for value in source_list:
            if isinstance(value, dict):
                yield (dict(cls._marshal_dict(value)))
            elif isinstance(value, list):
                yield (list(cls._marshal_list(value)))
            elif hasattr(value, 'marshal'):
                yield (value.marshal())
            else:
                yield value

class JSONAPIResponseMaker(APIResponseMaker):
    RESPONSE_HEADERS = {
        'Content-Type': 'application/json; charset=utf-8'
    }

    def make_response(self, **kwargs):
        response_dict = dict(self._marshal_dict(kwargs))
        response_text = json.dumps(response_dict, ensure_ascii=False, encoding='utf8')

        response = flask.make_response(response_text)
        response.headers.extend(self.RESPONSE_HEADERS)
        return response

class APIBlueprint(Blueprint):
    API_RESPONSE_MAKER_DICT = {
        'json': JSONAPIResponseMaker()
    }

    def make_response(self, **kwargs):
        api_response_maker = self.API_RESPONSE_MAKER_DICT['json']
        return api_response_maker.make_response(**kwargs)

class PageResponseMaker(object):
    def make_response(self, **kwargs):
        if 'page' in kwargs:
            return render_template(kwargs['page'])
        else:
            return render_template('index.html')

class PageBlueprint(Blueprint):
    def make_response(self, **kwargs):
        response_maker = PageResponseMaker()
        return response_maker.make_response(**kwargs)


