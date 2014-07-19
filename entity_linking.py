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

PREFIX = "http://keg.cs.tsinghua.edu.cn/instance/"
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
        return self.generate_newtext()

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
            candidates = self.db.get_candidateset(q.text)
            if candidates:
                q.entity_id = Disambiguation(q.text, self.text, candidates ).get_best()
                q.entity_uri = PREFIX+q.entity_id
                q.entity_url = XLORE_URL_PREFIX+q.entity_uri
            else:
                self.queries.remove(q)

    def generate_newtext(self):
        for i in range(len(self.queries)):
            q = self.queries[i]
            if q.entity_id:
                self.text = self.text[0:q.start] + "[[" + self.text[q.start:q.end+1] + "|" + q.entity_id + "]]" + self.text[q.end:]
        #        if i+1 < len(self.queries):
        #            self.queries[i+1].start = self.queries[i+1].start + 5+ len(q.entity_id) -1
        #            self.queries[i+1].end = self.queries[i+1].end + 5+ len(q.entity_id) -1
            else:
                self.text = self.text[0:q.start] + "[[" + self.text[q.start:q.end+1]  + "]]" + self.text[q.end:]
        #        if i+1 < len(self.queries):
        #            self.queries[i+1].start = self.queries[i+1].start + 4 -1
        #            self.queries[i+1].end = self.queries[i+1].end + 4 -1

        return self.text

class QueryEL():

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
        self.entities = []
        self.limit = args["limit"] if args.has_key("limit") else None
        self.db = None
        self.xlore = None

    def run(self):
        self.queries.append(Query(self.query_str, 0, 0))
        self.get_entity()
        if self.no_entity():
            self.queries = []
            w_num = len(self.query_str.split())
            if w_num >= 5: # extract terminology
                print "Extract terminology"
                self.extract_mentions()
                self.get_entity()
            if self.no_entity() and w_num >= 3 and w_num <=5: # split query string into short substring
                print "Split Query string"
                self.split_querystr()
                self.get_entity()

    def set_db(self, db):
        """
        Set Candidateset Mysql db
        """
        self.db = db

    def set_xlore(self, x):
        self.xlore = x

    def no_entity(self):
        return True if len(self.entities) == 0 else False

    def extract_mentions(self):
        te = TermExtractor()
        terms = te.get_terms(1, self.query_str)
        if len(terms) == 0:
            self.queries.append(Query(self.query_str, 0, 0))
        else:
            for t in terms:
                q = Query(t.lower(), 0, 0)
                self.queries.append(q)
            
        print "%d mentions"%len(self.queries)

    def split_querystr(self):
        ws = self.query_str.split()
        for i in range(1,len(ws)-1):
            new_query = " ".join(ws[i:])
            self.queries.append(Query(new_query, 0, 0))

    def get_entity(self):
        candidates = []
        for q in self.queries:
            print "Query String:",q.text
            candidates = self.db.get_candidateset(q.text)
            print "length of candidates",len(candidates)
            if candidates:
                print candidates
                if self.text and len(self.text) > 0:
                    es = Disambiguation(self.query_str, self.text, candidates ).get_best()
                else:
                    #if no session context, return the most similar title entity
                    if len(self.queries) > 1:
                        es = Disambiguation(q.text, self.query_str, candidates).get_best_use_freq(1)
                    else:
                        es = Disambiguation(q.text, self.query_str, candidates).get_best_use_freq(3)
                for e in es:
                    l = e.split("###")
                    t = l[0]
                    u = l[-1]
                    if len(u) > 0:
                        le = self.xlore.get_littleentity(u, self.lan)
                    else:
                        le = self.db.get_littleentity(t)
                    #if e.isdigit():
                    #    le = self.xlore.get_littleentity(e, self.lan)
                    #else:
                    #    le = self.db.get_littleentity(e)

                    self.entities.append(LittleEntity(**le))

def loadCandidateSet():
    global Candidateset
    Candidateset = dict()
    print "Candidateset loading..."
    for line in open("../../data/Mention2Entity.ttl"):
        line = line.strip("\n").strip("\r")
        Candidateset[line.split(":::")[0].lower()] = [ i[i.index('<')+1 : i.index('>')] for i in line.split(":::")[1].split("::;")[:-1]]

def loadURIToAbstract(candidates):
    #global Entity2Abstract
    URI2Abstract = dict()
    print "Entity to abstract loading..."
    for line in open("./data/enwiki-abstract.dat"):
        line = line.strip("\n").strip("\r")
        e = line.split("\t")[0].lower()
        if Entity2URI.has_key(e):
            uri = Entity2URI[e]
        if uri in candidates:
            print "uri:",uri,"in candidates"
            URI2Abstract[uri] = line.split("\t")[1]
    return URI2Abstract

def loadAbstract():
    print "Abstract loading..."
    count = 5
    for line in open("./data/abstract.txt"):
        if count < 0:
            break
        a = line.strip("\n").strip("\r")
        yield a
        count -= 1

def loadEntity2URI():
    global Entity2URI
    Entity2URI = dict()
    print "Title to URI..."
    for line in open("./data/loreEnwikiTitleURI.dat"):
        title, uri = line.strip("\n").split("\t\t")
        title = title.lower()
        uri = uri.split("/")[-1]
        Entity2URI[title] = uri
        
def loadURI2Entity():
    global URI2Entity
    URI2Entity = dict()
    print "URI to Title..."
    for line in open("./data/loreEnwikiTitleURI.dat"):
        title, uri = line.strip("\n").split("\t\t")
        title = title.lower()
        uri = uri.split("/")[-1]
        URI2Entity[uri] = title


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

    #################### Query Test #####################33
    db = MySQLDB()
    xlore = Xlore()
    l = ["data mining and social network"]
    for i in l:
        param = {}
        param['type']  = 'query'
        param['limit'] = 0
        param['text']  = ""
        param['t']     = datetime.datetime.now()
        param['query_str'] = i
        e = QueryEL(param)
        e.set_db(db)
        e.set_xlore(xlore)
        e.run()

        for entity in e.entities:
            print entity

