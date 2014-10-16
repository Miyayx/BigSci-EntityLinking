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

def normalize(d):
    a = d.values()
    n = len(a)
    mean = sum(a) / n
    std = math.sqrt(sum((x-mean)**2 for x in a) / n)

    for k, v in d.items():
        meanRemoved = v - mean #减去均值  
        stded = meanRemoved / (std+1) #用标准差归一化  
        d[k] = stded
    return d

################# Strategy ####################
def context_sim(mention, cans, doc, db, num=0, threshold=None):
    """
    Compare context of comment and abstract of entity 
    """
    c_sim = {}
    
    def similar_cal(t, cans):
#         print ("candiates:" + ' '+candidates)
        for c in cans:
            print (c)
            a = db.get_abstract(c)
            if a:
                print (c+' ' +'has abstract')

                seg_list = jieba.cut(t, cut_all=False)
                t = " ".join(seg_list)
                seg_list = jieba.cut(a, cut_all=False)
                a = " ".join(seg_list)

                try:
                    c_sim[c] = similarity(t, a)
                except:
                    c_sim[c] = 0.0


                for k,v in c_sim.items():
                    print (k +' ' + str(v))
            else:
                c_sim[c] = 0.0

    def similarity(t1, t2):
        return Distance.cosine_distance(t1.lower(), t2.lower());
    #if len(self.candidates) == 1:
    #    return self.candidates[0]

    similar_cal(doc, cans)

    if threshold:
        for k,v in c_sim.items():
            if v < threshold:
                c_sim.popitem(k)

    return c_sim


def entity_cooccur(db, mention, mentions, context_mentions,cans, threshold=None):
    """
    """

    c_sim = {}
    mentions = set(mentions)
    context_mentions = set(context_mentions)

    for c in cans:
        print ("Can ID:"+c)
        es = db.get_prop_entities(c)
        print ("    Entities in graph:")
        print ("    "+",".join(es))
        if not es or len(es) == 0:
            c_sim[c] = 0.0
        else:
            print ("    common: "+",".join(set(context_mentions)&set(es)))
            c_sim[c] = len(set(context_mentions)&set(es))

    for k,v in c_sim.items():
        print (k+" "+str(v))
        #c_sim[k] = v*1.0/len(mentions)
        c_sim[k] = v*1.0/len(context_mentions)

    if threshold:
        for k,v in c_sim.items():
            if v < threshold:
                c_sim.pop(k)

    return c_sim

def frequency(can_db, mention, cans)
    """
    Choose the most hit one 
    """

    c_sim = {}

    can_count = can_db.get_candidate_and_count(mention)
    new_can_count = dict((k, can_count[k]) for k in cans if can_count[k] > 1)

    if len(new_can_count) > 0:
        can_count = new_can_count

    for k,v in can_count.items():
        print k,v

    r = []
    for c in c_c:
        if self.is_in_domain(c[0]):
            print c[0],"is in domain"
            r.append(c[0])
        if len(r) == num:
            break
    if len(r) == 0:
        return [c[0] for c in c_c[:num]]
    return r


def title_editdistance(db, mention, cans):
    """
    Calculate the edit distance between two titles and get the most similar ones
    """

    c_sim = {}

    for c in cans:
        t = db.get_en_title(c)
        c_sim[c] = Distance.levenshtein(mention, t)

    return c_sim


class Disambiguation():

    def __init__(self, func=None, args = {}):

        if not func:
            raise ValueError("Not add strategy")
        self.func = func
        self.args = args

    def get_best(self):
        """
        return the highest score entity
        """

        if len(self.candidates) == 1:
            return self.candidates

        import operator
        c_sim = self.func(**self.args)
        if len(c_sim) == 0:
            return {}
        best = max(c_sim.iteritems(), key=operator.itemgetter(1))
        return [best]

    def get_sorted_cans(self, num=0):
        """
        Returns:
            return all candidate with their similarity
        """

        c_sim = self.func(**self.args)

        best = sorted(c_sim.items(), key=lambda x:x[1], reverse=True)
        if num:
            return best[:num]
        else:
            return best
        

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


