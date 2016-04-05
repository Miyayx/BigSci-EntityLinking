#/usr/bin/env python
#-*-coding=utf-8-*-

from model.query import Query
from model.searchitem import SearchItem
from db import *
from disambiguation import *

"""
This is a search interface 
"""

class ItemSearch():

    def __init__(self, args):
        self.query_str = args["q"] if args.has_key("q") else None
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
        self.limit = args["limit"] if args.has_key("limit") else 10 #这里跟query_el很不一样哦
        self.candb = None
        self.graph = None

    def run(self):
        self.queries = []
        self.queries.append(Query(self.query_str, -1))
        self.get_entity()
        for q in self.queries:
            if len(q.entities):
                self.entities.extend(q.entities)

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

    def get_entity(self):
        cans = []
        for q in self.queries:
            cans = self.candb.get_candidateset(q.text)
            print "length of candidates",len(cans)
            if cans and len(cans) > 0:
                print cans
                args = {
                        "can_db": self.candb,
                        "mention": q.text,
                        "cans": cans
                        }

                d = Disambiguation(frequency, args) #frequency是一个函数

                can_sim = d.get_sorted_cans(num=self.limit)

                for e_id, sim in can_sim:
                    le = self.graph.create_littleentity(e_id, self.lan)
                    le['type'] = ''
                    le.pop('related_item')
                    e = SearchItem(**le)
                    q.entities.append(e)


if __name__=="__main__":
    import datetime

    #################### Query Test #####################33
    db = MySQLDB()
    xlore = Xlore()
    l = ["svm", "data mining", "machine learning" ,"deep learning", "深度学习"]
    for i in l:
        param = {}
        param['limit'] = 0
        param['q'] = i
        e = ItemSearch(param)
        e.set_candb(db)
        e.set_graph(xlore)
        e.run()

        for entity in e.entities:
            print entity.__dict__

