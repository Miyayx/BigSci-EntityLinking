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
        self.origin = args["text"]
        self.text = args["text"]
        self.limit = args["limit"]
        self.queries = []
        self.threshold = 0
        self.db = None

    def run(self):
        self.extract_mentions()
        self.get_entity()
        for q in self.queries:
            print str(q)
        self.get_entity()

    def set_db(self, db):
        self.db = db

    def extract_mentions(self):

        te = TermExtractor()
        for t in te.get_terms(1,self.text):
            try:
                index = self.text.index(t)
                q = Query(t.lower(), index, index+len(t) )
                self.queries.append(q)
            except ValueError,e:
                print "Substring:",t,"is not in string"
            
        print "Find %d mentions"%len(self.queries)

    def get_entity(self):
        for q in self.queries:
            q.entities = []
            cans = self.db.get_candidateset(q.text)
            q.candidates = cans

            if cans:
                print ("candidate of " +q.text)

                args = {
                        }
                d = Disambiguation()

                can_sim = d.get_best()

                q.entity_uri = PREFIX + "instance/"+q.entity_id
                q.entity_url = XLORE_URL_PREFIX+q.entity_uri
            else:
                self.queries.remove(q)


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

