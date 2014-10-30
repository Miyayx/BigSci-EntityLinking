#/usr/bin/python2.7
#encoding=utf-8

import nltk
import string

from collections import Counter

from model.query import Query
from model.little_entity import LittleEntity
from term_extraction import TermExtractor
from db import *
from disambiguation import *

PREFIX = "http://keg.cs.tsinghua.edu.cn/"
XLORE_URL_PREFIX="http://xlore.org/sigInfo.action?uri="

class AbstractEL():
    
    def __init__(self, args):
        #print "Abstract", text
        self.text = args["text"] 
        self.limit = args["limit"] if args.has_key('limit') else 1
        self.queries = []
        self.threshold = 0
        self.db = None

    def run(self):
        self.extract_mentions()
        self.get_entity()
        for q in self.queries:
            print str(q)
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

    def extract_mentions(self):

        te = TermExtractor()
        for t in te.get_terms(1,self.text):
            try:
                index = self.text.index(t)
                q = Query(t.lower(), index)
                self.queries.append(q)
            except ValueError,e:
                print "Substring:",t,"is not in string"
            
        print "Find %d mentions"%len(self.queries)

    def get_entity(self):
        for q in self.queries:
            cans = self.candb.get_candidateset(q.text)
            q.candidates = cans

            print "length of candidates",len(cans)
            if cans and len(cans) > 0:
                #If section context exists
                ####### context_sim ##########
                print self.graph
                args = {
                        "mention" : q.text, 
                        "cans": cans, 
                        "doc" : self.text,
                        "db"  : self.graph,
                        "threshold": None
                        }

                d = Disambiguation(context_sim, args)

                can_sim = d.get_sorted_cans(self.limit)

                for e_id, sim in can_sim:
                    le = self.graph.create_littleentity(e_id, "en")
                    e = LittleEntity(**le)
                    e.sim = sim
                    q.entities.append(e)
            #else:
            #    self.queries.remove(q)

if __name__=="__main__":
    import datetime

    #################### Abstract Test #####################33
    ##loadCandidateSet()
    #loadEntity2URI()
    ##loadURI2Entity()
    ##loadEntityToAbstract()
    #db = MySQLDB()
    #with open("new_abstract.txt","w") as f:
    #    for a in loadAbstract():
    #        param = {}
    #        param['type'] = 'abstract'
    #        param['paper_id'] = 0
    #        param['limit'] = 0
    #        param['text'] = a
    #        param['t'] = datetime.datetime.now()
    #        e = AbstractEL(param)
    #        e.set_db(db)
    #       
    #        f.write(e.text+"\n\n")
    #        e.run()
    #        for q in e.queries:
    #            f.write(str(q))
    #        f.write("\n")

