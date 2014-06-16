#!/usr/lib/env/python2.7
#-*-coding:UTF-8-*-

import urllib2
import urllib
from datetime import datetime
import simplejson

"""
request:
    abstract:
    {
        type     : "abstract",
        paper_id : paper_id(int),
        text     : abstrct_text,
        limit    : the max num of returned entities 
        t        : time
    }

    query:
    {
        type     : "query", 填"query"
        query_str: query string,查询字符串
        text     : context of query，查询上下文（暂不考虑）
        limit    : the max num of related entities,返回的entity数量
        t        : time
    }

response: format:json:
    abstract:
    {
        paper_id : paper_id(int),
        text     : formatted abstract,
        t        : time,
        entity:[
            {
                query     : entity mention,
                start     : start index
                end       : end index
                entity_uri:
                similarity: value of similarity
            },
            {
                ...
            },...
        ]
    }

    query:
    {
        query_str : string of query,查询字符串
        t         : time           ,处理时间
        entity:[
            {
                title     : entity title,         
                abstract  : entity abstract,
                image     : urls of entity picture, 可以返回多个图片地址
                sim       : value of similarity
            },{
                ...
            },...
        ]
    }

"""

#URL = 'http://localhost:5656/linking'
#URL = 'http://166.111.68.66:5656/linking'
URL = 'http://10.1.1.23:5656/linking'

def abstract_test():
    param = {}
    param['type'] = 'abstract'
    param['paper_id'] = 0
    param['limit'] = 0

    count = 20
    for line in open("../../data/abstract.txt"):
        if count < 0:
            break
        a = line.strip("\n").strip("\r")

        param['text'] = a
        count -= 1
        param['t'] = datetime.now()

        try:
            f = urllib2.urlopen(URL, urllib.urlencode(param))
            resp = f.read()
            print resp
        except:
            print "Error!"

def query_test():
    param = {}
    param['type'] = 'query'
    param['query_str'] = 'machine learning'
    param['text'] = ''
    param['limit'] = 0
    param['t'] = datetime.now()
    f = urllib2.urlopen(URL, urllib.urlencode(param))
    #f = urllib2.urlopen(URL)
    resp = f.read()
    print f.headers
    print resp

if __name__=="__main__":
    #abstract_test()
    query_test()
