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
        type     : "query",
        query_str: query string,
        text     : context of query
        limit    : the max num of related entities
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
        query_str : string of query,
        t         : time
        entity:[
            {
                title     : entity title,
                abstract  : entity abstract,
                pic       : url of entity picture,
                sim       : value of similarity
            },{
                ...
            },...
        ]
    }

"""

URL = 'http://localhost:8880/linking'

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
    resp = f.read()
    print resp

if __name__=="__main__":
    abstract_test()
    #query_test()
