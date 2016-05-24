#/usr/bin/env python
#-*-coding=utf-8-*-

from model.query import Query
from model.searchitem import SearchItem
from db import *

"""
return entity according to specific uri id
"""

class UriEL():

    def __init__(self, args):
        self.query_uri = args["uri"] if args.has_key("uri") else None
        self.candb = None
        self.graph = None
        self.entity = None

    def run(self):
        self.entity = self.graph.create_academic_entity(self.query_uri, "all")

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

if __name__=="__main__":
    import datetime

    #################### Query Test #####################33
    db = MySQLDB()
    xlore = Xlore()
    l = [2,3,4,5]
    for i in l:
        param = {}
        param['uri'] = str(i)
        e = UriSearch(param)
        e.set_candb(db)
        e.set_graph(xlore)
        e.run()

