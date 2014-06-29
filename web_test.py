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
        lan      : "en" or "ch" or "all"(==None)
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

    query:
    {
        query_str : string of query,查询字符串
        t         : time           ,处理时间
        entity:[
            {
                entity_id : entity id in Xlore
                uri       : entity uri in Xlore
                url       : entity url in XLore
                title     : entity title,     {"en":"","ch",""}    
                abstract  : entity abstract,  {"en":"","ch":""}
                image     : urls of entity picture, 可以返回多个图片地址
                sim       : value of similarity
            },{
                ...
            },...
        ]
    }

"""

URL = 'http://localhost:5655/linking'
#URL = 'http://166.111.68.66:5656/linking'
#URL = 'http://10.1.1.23:5656/linking'

def abstract_test():
    param = {}
    param['type'] = 'abstract'
    param['paper_id'] = 0
    param['limit'] = 0

    count = 20
    for line in open("data/abstract.txt"):
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

def querylog_test(logfn, hitfile=None, statisfile=None):
    import time
    import json
    times = []
    count = 0
    hit = 0
    min_time = 100000000
    max_time = 0
    ch = 0
    en = 0
    not_hit = []
    if hitfile:
        hitf = open(hitfile,"w")
    if statisfile:
        statisf = open(statisfile,"w")
    #result_file = open("./data/querylog_test_hit_result.dat","w")
    for keyword in open(logfn):
        count += 1
        keyword = keyword.strip("\n").strip("\r")
        keyword = keyword.replace('"','')
        start = time.time()
        try:
            r = query_test(keyword)
        except Exception,e:
            print "Error, keyword:",keyword
            print e
            continue

        # if hit
        j = json.loads(r)
        if len(j["entity"]) > 0:
            hit += 1
            print keyword
            print r
            hitf.write(keyword+"\t")
            hitf.write("Hit\t")
            try:
                hitf.write(j["entity"][0]["title"]["en"]+"\t")
            except:
                print  j["entity"][0]["title"]["en"]
            hitf.write(j["entity"][0]["url"]+"\n")
    #        result_file.write(keyword+"\n")
    #        result_file.write(r+"\n")
    #        result_file.write("\n")
            if not j["entity"][0]["title"]["en"] == "null":
                en += 1
            if not j["entity"][0]["title"]["ch"] == "null":
                ch += 1
        else:
            hitf.write(keyword+"\t")
            hitf.write("NOT Hit\n")
            not_hit.append(keyword)

        duration = time.time()-start
        print "Time:",duration
        if duration < min_time:
            min_time = duration
        if duration > max_time:
            max_time = duration

        times.append(duration)

    #result_file.close()
    hitf.close()

    print "Avg time:", sum(times)/len(times)
    print "Max time:", max_time
    print "Min time:", min_time
    print "Hit:",hit
    ratio = (hit*1.0)/count
    print "Hit Ratio:",ratio

    if statisf:
        statisf.write("Total: "+str(count))
        statisf.write("Hit: "+str(hit))
        statisf.write("Hit Ratio: "+str(ratio))
        statisf.write("Has En title:"+str(en))
        statisf.write("Has Ch title:"+str(ch))
        statisf.write("Avg time: "+ str(sum(times)/len(times)))
        statisf.write("Max time: "+str(max_time))
        statisf.write("Min time: "+str(min_time))
        statisf.write("Hot Hit List:"+"\n")
        statisf.write(str(not_hit))
        statisf.close()

    return hit,ratio

if __name__=="__main__":
    #abstract_test()

    #querylog_test("./data/query_keywords.dat")
    #querylog_test("./data/results/mention/Ner/1016.page")
    #querylog_test("./data/all_interest.dat")
    #querylog_test("./data/interest.dat","./test/interest_hit.csv","./test/interest_statis.dat");
    #querylog_test("./data/author_100.dat","./test/author_100_hit.csv","./test/author_100_statis.dat");

    querylog_test("./data/arnet_interest.dat","./test/interest_hit.csv","./test/interest_stat.dat");
    querylog_test("./data/arnet_author.dat","./test/author_hit.csv","./test/author_stat.dat");

    #for q in ['machine learning','data structure','data mining','Computer architecture']:
    #for q in ['data mining and machine learning',]:
    #    print query_test(q)
