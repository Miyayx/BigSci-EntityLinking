#/usr/bin/env python
#-*-coding:utf-8-*-

from db import *
import urllib2
import urllib
from datetime import datetime
import codecs

URL = 'http://10.1.1.23:5656/linking'

def query_test(q):
    param = {}
    param['type'] = 'query'
    param['query_str'] = q
    param['text'] = ''
    param['limit'] = 0
    param['t'] = datetime.now()
    f = urllib2.urlopen(URL, urllib.urlencode(param))
    #f = urllib2.urlopen(URL)
    resp = f.read()
    return resp

with open("./result/academy_words2.dat",'w') as f:
    for line in open('./data/all_intetest.dat'):
        keyword = line.strip('\n')
        try:
            r = query_test(keyword)
        except Exception,e:
            print "Error, keyword:",keyword
            print e
            continue

        j = json.loads(r)
        if len(j["entity"]) > 0:
            f.write(j["entity"][0]["title"]['en'].encode('utf-8')+'\t'+j["entity"][0]["title"]['ch'].encode('utf-8')+'\n')

            f.flush()


