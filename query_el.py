#/usr/bin/env python
#-*-coding=utf-8-*-

import nltk
import string
import jieba.posseg as pseg
import re

from model.query import Query
from model.little_entity import LittleEntity
from db import *
from disambiguation import *
import stanford_parser 

"""
This is the entity linging for normal string
"""

class QueryEL():

    def __init__(self, args):
        self.query_str = args["query_str"] if args.has_key("query_str") else None
        try:
            self.query_str = self.query_str.decode('utf-8')
        except:
            pass
        self.text = args["text"] if args.has_key("text") else None
        if args.has_key("lan"):
            if args["lan"] == "en":
                self.lan = "en"
            elif args["lan"] == "ch":
                self.lan = "ch"
            else:
                self.lan = "all"
        else:
            self.lan = "all"

        self.queries = [] #list of text
        self.limit = args["limit"] if args.has_key("limit") else None
        self.candb = None
        self.graph = None

        self.en_parser = None
        self.zh_parser = None


    def run(self):
        self.queries = []

        if re.search(ur"[\u4e00-\u9fff]+", self.query_str):#Chinese
            self.lan = "ch"
            if len(self.query_str) > 5 :
                self.extract_zh_mentions(self.query_str)
            else:
                self.queries.append(Query(self.query_str, 0))
        else: #English or others
            if len(self.query_str.split()) > 3 :
                self.extract_en_mentions(self.query_str)
            else:
                self.queries.append(Query(self.query_str, 0))

        self.get_entity()

    def set_candb(self, db):
        """
        Set Candidateset Mysql db
        """
        self.candb = db

    def set_graph(self, x):
        """
        Set XLore db
        """
        self.graph = x

    def set_en_parser(self, p):
        self.en_parser = p

    def set_zh_parser(self, p):
        self.zh_parser = p

    def no_entity(self):
        return True if len(self.entities) == 0 else False

    def extract_en_mentions(self, s):
        """
        Usr Standford Parser and NLTK to extract mentions from english string
        """
        types = ['LOCATION','PERSON','ORGANIZATION']

        if not self.en_parser:
            self.en_parser = stanford_parser.Parser()
        seg_list = self.en_parser.NER(s)
        seg_index = []
        begin = 0
        last = 0
        i  = 0
        if type(seg_list[0]) == list: #不同系统上的返回结果格式不一样,我们想要的是[('word','LOCATION'),('people','PERSON')],但有的是[[('word','LOCATION')]],这种情况要把里面的list提取出来
            seg_list = seg_list[0]
        while i < len(seg_list):
            segs = []
            word, tag = seg_list[i]
            if tag in types:
                j = i
                # 属于指定类型，类型相同且连续的，合到一起
                while j < len(seg_list) and seg_list[j][1] == tag:
                    segs.append(seg_list[j][0])
                    j += 1
                i = j
                query = " ".join(segs)
                print "query:",query
                try:
                    begin = s.index(query, last)
                    print "Can't find %s"%query
                except:
                    continue
                last = begin + len(query)
                self.queries.append(Query(query, begin))
            else:
                #不属于指定类型，直接跳过
                i += 1
                #begin = s.index(word, last)
                #last = begin + len(word)

        print "%d mentions"%len(self.queries)

    def extract_zh_mentions(self, s):
        """
        Use jieba to extract mentions from Chinese string
        """

        types = ['nt','nr','nz','ns']

        seg_list = pseg.cut(s)
        seg_index = []
        last = 0
        for seg in seg_list:
            begin = s.index(seg.word, last)
            last = begin + len(seg.word)
            if seg.flag in types:
                self.queries.append(Query(seg.word.encode('utf-8'), begin))
            
        print "%d mentions"%len(self.queries)

    def get_entity(self):
        cans = []
        store = {}
        for q in self.queries:

            if q.text in store.keys():#如果已经查询过这个mention了
                q.entities = store[q.text].entities
                print q.text,"Hit"
                continue

            print "Query String:",q.text
            try:
                q.text = q.text.encode('utf-8')
            except:
                pass
            cans = self.candb.get_candidateset(q.text)
            print "length of candidates",len(cans)
            if cans and len(cans) > 0:
                if self.text and len(self.text) > 0:
                    #If section context exists
                    ####### context_sim ##########
                    args = {
                            "mention" : q.text, 
                            "cans": cans, 
                            "doc" : self.text,
                            "db"  : self.graph,
                            "threshold": None,
                            "lan":self.lan
                            }

                    d = Disambiguation(context_sim, args)
                else:
                    #if no session context, return the most similar title entity

                    args = {
                            "can_db": self.candb,
                            "mention": q.text,
                            "cans": cans
                            }

                    d = Disambiguation(frequency, args)

                can_sim = d.get_sorted_cans(self.limit)

                for e_id, sim in can_sim:
                    le = self.graph.create_littleentity(e_id, self.lan)
                    e = LittleEntity(**le)
                    e.sim = sim
                    q.entities.append(e)

                store[q.text] = q
            #else:
            #    self.queries.remove(q)


if __name__=="__main__":
    import datetime

    db = MySQLDB()
    xlore = Xlore()
    #l = ["I went to New York to meet John Smith"]
    #l = ["Micheal Jordan"]
    #l = ["machine learning"]
    l = ["data mining", "machine learning" ,"deep learning", "深度学习"]
    for i in l:
        param = {}
        param['type']  = 'query'
        param['limit'] = 3
        param['text']  = ""
        param['t']     = datetime.datetime.now()
        param['query_str'] = i
        e = QueryEL(param)
        e.set_candb(db)
        e.set_graph(xlore)

        p = stanford_parser.Parser()
        e.set_en_parser(p)

        e.run()

        for entity in e.queries:
            print entity

