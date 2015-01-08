#!/usr/bin/env python
#-*-coding:UTF-8-*-

import urllib
import urllib2
from datetime import datetime
import simplejson

"""
request:
    el for newsminer:
    {
        type     : "el",
        text     : context,
        query_str: query word
        limit    : the max num of returned entities 
        t        : time
    }

response: format:json:
    {
        text     : formatted context,
        t        : time,
        entity:[
            {
                query     : entity mention,
                start     : start index
                end       : end index
                entity_id : entity id  in Xlore
                entity_uri: entity uri in XLore
                entity_url: entity url in XLore
                similarity: value of similarity
            },
            {
                ...
            },...
        ]
    }
"""

URL = 'http://localhost:5656/linking'
#URL = 'http://166.111.68.66:5656/linking'
#URL = 'http://10.1.1.23:5656/linking'

def query_test():
    param = {}
    param['type'] = 'el'
    param['limit'] = 1

    count = 20
    for line in open("data/news.txt"):
        if count < 0:
            break
        a = line.strip("\n").strip("\r")

        param['text'] = a
        param['query_str'] = a
        count -= 1
        param['t'] = datetime.now()

        f = urllib2.urlopen(URL, urllib.urlencode(param))
        resp = f.read()
        print resp

if __name__=="__main__":
    query_test()
