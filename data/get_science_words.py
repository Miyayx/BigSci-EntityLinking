#!/usr/bin/python
#-*-coding:utf-8-*-

import os

def get_science_words():
    cate_ins = {}
    words = []
    print "Loading cate_ins"
    for line in open('/home/zigo/KnowledgeLinking/etc/enwiki-category-article.dat'):
        cate, ins = line.strip('\n').strip('\r').split('\t\t')
        cate_ins[cate.lower()] = ins.split(';')
    print "Get instance words"

    for fn in os.listdir('cate/'):
        for line in open(os.path.join('./cate',fn)):
            cate = line.strip('\n').strip('\r')
            if not cate_ins.has_key(cate):
                print "No Such Category:",cate
            else:
                words += cate_ins[cate]
    print "Delete cate_ins"
    del cate_ins
    words = set(words)
    print len(words),"words"

    result = []
    with open("../result/science_words.dat",'w') as f:
        u = ""
        for line in open('/home/lore4/rdfdb/loreInstanceList.ttl'):
            if not line.startswith('<'):
                continue
            _type = line[line.index('>')+1:]
            _type = _type.split(':')[0].strip()
            uri = line[line.index('<')+1:line.rindex('>')]
            title = line[line.index('"')+1:line.rindex('"')]
            if _type == "enwiki" and title in words:
                u = uri
                result = []
                print title
                result.append(title)
            if u == uri and not _type == "enwiki" and len(result) == 1:
                result.append(title)
                print title
                f.write("\t".join(result)+"\n")
                f.flush()
        

get_science_words()

