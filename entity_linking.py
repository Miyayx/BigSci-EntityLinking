#/usr/bin/python2.7
#encoding=utf-8

import nltk
import string

from collections import Counter

from query import Query

class EntityLinking():
    
    def __init__(self, text):
        print "Abstract", text
        self.text = text
        self.queries = []
        self.threshold = 0

    def run(self):
        self.extract_mentions(Candidateset.keys())
        self.get_entity()
        return self.generate_newtext()

    def extract_mentions(self, cand_ms):
        index = 0
        words = self.text.split()
        while index < len(words):
            print "index",index
            for i in [5,4,3,2,1]:
                m = words[index:index+i].lower()
                if m in cand_ms:
                    print m
                    q = Query(m, index, i)
                    self.queries.append(q)
                    index = i
                    break
            index += 1
        print "Find %d mentions"%len(self.queries)

    def get_entity(self):
        for q in self.queries:
            q.entity_id = Disambiguation(self.text, q).best_entity

    def generate_newtext(self):
        for q in self.queries:
            self.text = self.text[0:q.start] + "[[" + replace(self.text[q.start:q.end], q.entity_id) + "]]" + self.text[q.end:]
        return self.text

class Disambiguation():

    def __init__(self, t, q):
        self.best_entity = self.choose_best(t, q)

    def choose_best(self):
        candidates = Candidateset[q.text]
        Entity2Abstract = loadEntityToAbstract(candidates)
        similar = [similarity(t,Entity2Abstract[c]) for c in candidates]
        similar = [s if s > threshold else None for s in similar]
        best = max(similar)
        return c[similar.index(best)] if not best == None else None

    def similarity(self, t1, t2):
        
        def cosine_distance(u, v):
            """
            Returns the cosine of the angle between vectors v and u. This is equal to u.v / |u||v|.
            """
            return numpy.dot(u, v) / (math.sqrt(numpy.dot(u, u)) * math.sqrt(numpy.dot(v, v)))

        tp = TextProcesser()
        c1 = tp.get_count(t1)
        c2 = tp.get_count(t2)
        words = list(set(c1.keys()).add(c2.keys()))
        v1 = [c1.get(w,0) for w in words]
        v2 = [c2.get(w,0) for w in words]
        return cosine_distance(v1, v2)
        

class TextProcesser():

    def __init__(self, t):
        self.text = t

    def get_tokens(self):
        lowers = self.text.lower()
        #remove the punctuation using the character deletion step of translate
        no_punctuation = lowers.translate(None, string.punctuation)
        tokens = nltk.word_tokenize(no_punctuation)
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
        Candidateset[line.split(":::")[0].lower()] = line.split(":::")[1].split("::;")[:-1]

def loadEntityToAbstract(candidates):
    #global Entity2Abstract
    Entity2Abstract = dict()
    print "Entity to abstract loading..."
    for line in open("../../data/enwiki-abstract.dat"):
        line = line.strip("\n").strip("\r")
        e = line.split("\t")[0]
        if e in candidates:
            Entity2Abstract[e] = line.split("\t")[1]
    return Entity2Abstract

def loadAbstract():
    print "Abstract loading..."
    count = 5
    for line in open("../../data/abstract.txt"):
        if count < 0:
            break
        a = line.strip("\n").strip("\r")
        yield a
        count -= 1

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
            # 集合的 交 运算
            ids = ids & index.get(q, set())
        for id in ids:
            print article_map[id]


if __name__=="__main__":
    loadCandidateSet()
    #loadEntityToAbstract()
    for a in loadAbstract():
        e = EntityLinking(a)
        e.run()

