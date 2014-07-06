#!/usr/bin/python
#-*-coding:utf-8-*-

from nltk.corpus import stopwords

def get_outof_xlore_list(fold, fnew):
    newl = []
    olds = [line.strip("\n").split("\t\t")[1] for line in open(fold)]
    news = [line.strip("\n") for line in open(fnew)]
    l = list(set(news)-set(olds))
    stop = stopwords.words('english')
    for i in l:
        if i not in stop:
            newl.append(i)
    return newl

def import2mysql(l, conceptfn, abstractfn):
    d = dict((i,{"title":i,"url":"http://en.wikipedia.org/wiki/"+i.split().join("_")}) for i in l)
    db = MySQLDB()
    for line in open(conceptfn):
        ins,con = line.strip("\n").split("\t\t")
        d[ins]["super_topic"] = con
    for line in open(abstractfn):
        ins,a = line.strip("\n").split("\t\t")
        d[ins]["abstract"] = a
    
    for v in d.values():
        db.insert_wiki_entity(**v)
        

if __name__=="__main__":
    ws = get_outof_xlore_list("/home/zjt/enwikiMap/data/enInstIndex.ttl","/home/lsj/data/enwiki/enwiki-instanceList.dat")
    with open("../data/words_notin_xlore.dat","w") as f:
        for w in ws:
            f.write(w+"\n")
   


