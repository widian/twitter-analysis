#!/usr/bin/env python
# -*- coding:utf8 -*-
from keen.client import KeenClient
keen_client = KeenClient(
        project_id="55f93f85d2eaaa05a699de39",
        write_key="8f77f837b629b8519e8d23c541fedc42d423f8f71dc10e2244b50e364e7034cb753d960ea31d7925d044a109233cdf55e88792d4fa9f16f4e2410a7e09309242565415ef3d7299526c2fbf6860603bd349d186f068f5bd940ff047c2f4a4f0959c1cda4c3c3208729524b233b096e4de",
        read_key="2f1b89a70f545caaeff7964b5daa60236844aa0291a20749e15ca83e30c63d3cb939d7eb720666c03164403680d77d8e6086e3f1d60b5a34f696b09fc1bd695a0a0f0a1f947757cd5bd5666d5448b614e9928a544bfcecfe4bb9e52b1c02d77e49e359c04dc2dd901764097364b00573",
        master_key="3855C83BD7B0720323E0B1E447149B01")

class Keen(object):
    keen = None
    def __init__(self):
        self.keen = keen_client

    def add_girl(self, collection, name, count_dict, **kwargs):
        data_array = list()
        for i in count_dict.keys():
            if self.is_exist_girl(collection, name, i):
                pass
            else:
                data_dict = dict()
                data_dict["캐릭터"] = name
                data_dict["keen"] = dict()
                data_dict["count"] = count_dict[i]
                data_dict["keen"]["timestamp"] = i
                data_array.append(data_dict)
        self.keen.add_events({
            collection : data_array})
        return True

    def is_exist_girl(self, collection, name, timestamp, **kwargs):
        return self.keen.count(collection, filters=[{"property_name" : "keen.timestamp", "operator" : 'eq', "property_value" : timestamp}]) != 0

    def test_function(self, **kwargs):
        self.keen.add_events({
            "test_cases" : [
                {"user_name" : "nameuser4",
                    "keen" : {
                        "timestamp" : "2015-09-14T02:09:10.141Z"
                        },
                    "count" : 7
                    },
                {"user_name" : "nameuser5",
                    "keen" : {
                        "timestamp" : "2015-09-14T02:09:10.141Z"
                        },

                    "count" : 4}]
                })
        return self.keen.count("test_cases", timeframe="this_14_days")
