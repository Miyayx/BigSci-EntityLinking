#/usr/bin/python2.7
#encoding=utf-8

import nltk
import string

from collections import Counter

from query import Query
from term_extraction import TermExtractor
from db import *
from little_entity import LittleEntity

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
                q.entity_id = Disambiguation(self.text, candidates ).get_best()
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
        #self.extract_mentions()
        self.queries.append(Query(self.query_str, 0, 0))
        self.get_entity()

    def set_db(self, db):
        self.db = db

    def set_xlore(self, x):
        self.xlore = x

    def extract_mentions(self):
        mentions = db.get_mentions()
        for m in mentions:
            d = Distance.levenshtein(self.query_str, m)
            if d < 10:
                q = Query(m, 0, 0)
                self.queries.append(q)

        print "Find %d mentions"%len(self.queries)

    def get_entity(self):
        candidates = []
        for q in self.queries:
            print q.text
            candidates += self.db.get_candidateset(q.text)
        print "length of candidates",len(candidates)
        if candidates:
            if self.text:
                es = Disambiguation(self.text, candidates ).get_best()
            else:
                #if no session context, return the most similar title entity
                es = Disambiguation(self.query_str, candidates).get_best_use_title(3)
            for e in es:
                le = self.xlore.get_littleentity(e, self.lan)
                self.entities.append(LittleEntity(**le))

class Disambiguation():

    def __init__(self, t, candidates):
        self.text = t
        self.candidates = candidates
        self.c_sim = {}
        self.threshold = 0.9
        #self.similar_cal(t, candidates)

    def get_best_use_title(self, num = 0):
        """
        Calculate the edit distance between two titles and get the most similar ones
        """

        if len(self.candidates) == 1:
            return self.candidates[0]

        for c in self.candidates:
            t = Xlore().get_en_title(c)
            self.c_sim[c] = Distance.levenshtein(self.text, t)

        import operator
        if num <= 1 or not num:
            best = min(self.c_sim.iteritems(), key=operator.itemgetter(1))[0]
            
        else:
            best = sorted(self.c_sim.keys(), key=self.c_sim.get)[:num]
        return best

    def get_best(self, num = 0):
        #candidates = Candidateset[q.text]
        if len(self.candidates) == 1:
            return self.candidates[0]

        self.similar_cal(self.text, self.candidates)

        import operator
        if num <= 1 or not num:
            best = max(self.c_sim.iteritems(), key=operator.itemgetter(1))[0]
            
        else:
            best = max(self.c_sim.iteritems(), key=operator.itemgetter(1))[:num]
        return best

    def similar_cal(self, t, candidates):
        print "candiates:",candidates
        #URI2Abstract = loadURIToAbstract(candidates)
        for c in candidates:
            print c
            a = Xlore().get_abstract(c)
            if a:
                print c,"has abstract"
                #similar.append(self.similarity(t, URI2Abstract[c]))
                self.c_sim[c] = self.similarity(str(t), str(a))
            else:
                self.c_sim[c] = None
        #similar = [self.similarity(t, URI2Abstract[c]) for c in candidates]
        #similar = [self.similarity(q.text, URI2Entity[c]) for c in candidates]
        #similar = [s if s > self.threshold else None for s in similar]

    def similarity(self, t1, t2):
        return Distance.cosine_distance(t1.lower(), t2.lower());
        
class Distance():

    @staticmethod
    def cosine_distance(t1, t2):
        """
        Return the cosine distance between two strings
        """

        def cosine(u, v):
            """
            Returns the cosine of the angle between vectors v and u. This is equal to u.v / |u||v|.
            """
            import numpy
            import math
            return numpy.dot(u, v) / (math.sqrt(numpy.dot(u, u)) * math.sqrt(numpy.dot(v, v)))

        tp = TextProcesser()
        c1 = dict(tp.get_count(t1))
        c2 = dict(tp.get_count(t2))
        keys = c1.keys() + c2.keys()
        word_set = set(keys)
        words = list(word_set)
        v1 = [c1.get(w,0) for w in words]
        v2 = [c2.get(w,0) for w in words]
        return cosine(v1, v2)

    @staticmethod
    def levenshtein(first, second):
        """
        Edit Distance
        """
        if len(first) > len(second):
            first,second = second,first
        if len(first) == 0:
            return len(second)
        if len(second) == 0:
            return len(first)
        first_length = len(first) + 1
        second_length = len(second) + 1
        distance_matrix = [range(second_length) for x in range(first_length)]
        #print distance_matrix 
        for i in range(1,first_length):
            for j in range(1,second_length):
                deletion = distance_matrix[i-1][j] + 1
                insertion = distance_matrix[i][j-1] + 1
                substitution = distance_matrix[i-1][j-1]
                if first[i-1] != second[j-1]:
                    substitution += 1
                distance_matrix[i][j] = min(insertion,deletion,substitution)
        return distance_matrix[first_length-1][second_length-1]


class TextProcesser():

    def __init__(self):
        pass

    def get_tokens(self, t):
        lowers = t.lower()
        #remove the punctuation using the character deletion step of translate
        no_punctuation = lowers.translate(None, string.punctuation)
        tokens = nltk.word_tokenize(no_punctuation)
        from nltk.corpus import stopwords
        tokens = [w for w in tokens if not w in stopwords.words('english')]
        return tokens

    def stem_tokens(self, tokens, stemmer):
        stemmed = []
        for item in tokens:
            stemmed.append(stemmer.stem(item))
        return stemmed

    def get_count(self, t):
        return Counter(self.get_tokens(t)).most_common()


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

# 建立倒排索引
def create_index():
    #  单词到对应的文章id
    # {'word': [1, 2, 3], 'the': [7, 9], 'active': [1]}
    index = {}
    for id, article in article_map.items():
        words = article.split()
        for word in words:
            word = word.lower()
            if word in index:
                index[word].add(id)
            else:
                index[word] = set([id])
    return index

def search_index(query):
    # 切词
    keywords = query.split()

    if keywords:
        ids = index.get(keywords[0], set())
        for q in keywords[1:]:
            #集合的交运算
            ids = ids & index.get(q, set())
        for id in ids:
            print article_map[id]


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
    l = ["machine learning","data structure","data mining"]
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

