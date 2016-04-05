#/usr/bin/env python
#-*-coding=utf-8-*-

import nltk
import string

from model.query import Query
from model.little_entity import LittleEntity
from term_extraction import TermExtractor
from db import *
from disambiguation import *

"""
This is the entity linking module for BigSci query
"""

class BigSciEL():

    def __init__(self, args):
        self.query_str = args["query_str"] if args.has_key("query_str") else None
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
        self.entities = [] #list of entities
        self.limit = args["limit"] if args.has_key("limit") else 1 #这里跟query_el很不一样哦
        self.candb = None
        self.graph = None

    def run(self):
        self.queries = []
        w_num = len(self.query_str.split())
        if w_num < 3:
            self.queries.append(Query(self.query_str, -1))
        if w_num >= 5: # extract terminology
            print "Extract terminology"
            self.extract_mentions()
        if self.no_entity() and w_num >= 3 and w_num <=5: # split query string into short substring
            print "Split Query string"
            self.split_querystr()

            if "-" in self.query_str:
                for q in self.query_str.split():
                    if "-" in q:
                        self.queries.append(Query(q, -1))
                        break

        self.get_entity()
        for q in self.queries:
            if len(q.entities):
                self.entities.append(q.entities[0])

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

    def no_entity(self):
        es = []
        for q in self.queries:
            es += q.entities
        return True if len(es) == 0 else False

    def is_in_domain(self, c):
        """
        If c(uri) is in specific domain
        """
        domain = ['100271','104436','100262','103549','100301','104859','105485','109406','100269']
        uris = self.graph.get_type_uri(c)
        for u in uris:
            if u in domain:
                return True
            else:
                path = self.candb.get_superpath(u)
                if not path:
                    continue
                for p in path.split("/"):
                    if p in domain:
                        return True
        return False

    def is_in_domain2(self, c):
        """
        If c(uri) is in specific domain
        67:Culture, 156:Science, 281:Personal life, 366:Nature, 80:Society, 431:Arts, 524:Technology, 235:Economies, 353:History, 271:People, 291:Geography, 180:Sports
        """
        #domain = ['156', '366', '524', '291']
        domain = ['156', '524', '291']
        
        uris = self.graph.get_topclass_from_ins(c)
        for u in uris:
            if u in domain:
                return True
        return False
    
    def extract_mentions(self):
        """
        Extract terminology from query string
        """
        te = TermExtractor()
        terms = te.get_terms(1, self.query_str)
        if len(terms) > 0:
            for t in terms:
                q = Query(t.lower(), -1)
                self.queries.append(q)
            
        print "%d term mentions"%len(self.queries)

    def split_querystr(self):
        """
        Get sub query strings according to truncate the origin string
        """
        ws = self.query_str.split()
        for i in range(0,len(ws)-2):
            for j in range(2,len(ws)):
                new_query = " ".join(ws[i:j])
                self.queries.append(Query(new_query, -1))

    def get_entity(self):
        cans = []
        for q in self.queries:
            print "Query String:",q.text
            cans = self.candb.get_candidateset(q.text)
            print "length of candidates",len(cans)
            if cans and len(cans) > 0:
                print cans
                if self.text and len(self.text) > 0:
                    #If section context exists
                    ####### context_sim ##########
                    args = {
                            "mention" : q.text, 
                            "cans": cans, 
                            "doc" : self.comment,
                            "db"  : self.db,
                            "threshold": None
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

                can_sim = d.get_sorted_cans()

                r = []
                for c in can_sim:
                    #if self.is_in_domain2(c[0]):
                    #    print c,"is in domain"
                    r.append(c)
                    if len(r) == self.limit:
                        break

                can_sim = r

                for e_id, sim in can_sim:
                    le = self.graph.create_littleentity(e_id, self.lan)
                    e = LittleEntity(**le)
                    e.sim = sim
                    q.entities.append(e)
            #else:
            #    self.queries.remove(q)


if __name__=="__main__":
    import datetime

    #################### Query Test #####################33
    db = MySQLDB()
    xlore = Xlore()
    l = ["svm", "data mining", "machine learning" ,"deep learning", "深度学习"]
    for i in l:
        param = {}
        param['type']  = 'query'
        param['limit'] = 0
        param['text']  = ""
        param['t']     = datetime.datetime.now()
        param['query_str'] = i
        e = BigSciEL(param)
        e.set_candb(db)
        e.set_graph(xlore)
        e.run()

        for entity in e.entities:
            print entity

