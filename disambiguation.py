#!/usr/bin/python2.7
#-*-coding:utf-8-*-

import nltk
import string
import math

from collections import Counter

from model.query import Query
from model.little_entity import LittleEntity
from term_extraction import TermExtractor
from db import *
from wiki_miner import *

class Disambiguation():

    def __init__(self, m, d, candidates):
        self.mention = m
        self.doc = d
        self.candidates = candidates
        self.c_sim = {}
        self.threshold = 0.9
        #self.similar_cal(t, candidates)

    def domain_constrain(self):
        new_can = []
        for c in self.candidates:
            if c in domain:
                new_can.append(c)
        self.candidates = new_can

    def get_best_use_freq(self, num = 0):
        """
        Choose the most hit one 
        """

        if len(self.candidates) == 1:
            return self.candidates

        can_count = MySQLDB().get_candidate_and_count(self.mention)
        for k,v in can_count.items():
            print k,v
        c_c = sorted(can_count.iteritems(), key=lambda d:d[1], reverse = True)
        if num <= 1 or not num:
            return c_c[0][0]
        else:
            return [c[0] for c in c_c][:num]

    def get_best_use_title(self, num = 0):
        """
        Calculate the edit distance between two titles and get the most similar ones
        """

        if len(self.candidates) == 1:
            print "Has only one candidates "
            return self.candidates

        #self.domain_constrain()

        for c in self.candidates:
            t = Xlore().get_en_title(c)
            self.c_sim[c] = Distance.levenshtein(self.doc, t)

        import operator
        if num <= 1 or not num:
            best = min(self.c_sim.iteritems(), key=operator.itemgetter(1))[0]
            
        else:
            best = sorted(self.c_sim.keys(), key=self.c_sim.get)[:num]
        return best

    def get_best(self, num = 0):
        #candidates = Candidateset[q.text]
        if len(self.candidates) == 1:
            return self.candidates

        self.similar_cal(self.doc, self.candidates)

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

    def LINDEN(self, d, candidates):
        w = [1,1,1]
        feature = Feature(d)
        results = []
        for c in candidates:
            f1 = feature.link_probability(self.mention, c)
            f2 = feature.semantic_associativity(self.doc, c)
            f3 = feature.global_coherence(c)
            results.append(w[0]*f1, w[1]*f2, w[2]*f3)
        return candidates[results.index(max(results))]
        
class Feature():

    def __init__(self, d):
        self.d = d

    @staticmethod
    def WLM(e1, e2):
        """
        Wikipedia Link-based Measure
        """
        WHOLE = 7854301
        s1 = set(Xlore().get_innerLink(e1))
        s2 = set(Xlore().get_innerLink(e2))
        
        result =1-(math.log(max(len(s1),len(s2)))-math.log(len(s1^s2)))/(whole-math.log(min(len(s1),len(s2))))

        return result

    def max_link_prob_entity(m):
        import operator
        db = MySQLDB()
        e_c = db.get_all_link_count(m)
        if e_c:
            return max(e_c.iteritems(), key=operator.itemgetter(1))[0]
        else:
            return None

    def link_probability(m, e):
        db = MySQLDB()
        e_c = db.get_all_link_count(m)
        return e_c[e]/sum(e_c.values())

    def semantic_associativity(d, e):
        #concepts = Xlore().get_innerLink(de)
        en_text = WikiParser().find_entity(d)
        en_uri = [MySQLDB().get_direct_entity(t) for t in en_text]
        ass = [Feature.WLM(u, e) for u in en_uri]
        return sum(ass)/len(ass)

    def global_coherence(e):
        EM = []
        for m in mentions:
            em = self.max_link_prob_entity(m)
            if em:
                Em.append(em)
        ass = [Feature.WLM(em, e) for em in EM]
        return sum(ass)/len(ass)

        
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


