#!/usr/bin/python
#-*-coding:utf-8-*-

def get_science_words():
    cate_ins = {}
    words = []
    for line in open(''):
        cate, ins = line.strip('\n').split('\t')
        cate_ins[cate] = cate_ins.get(cate,[])+[ins]
    for line in open('./cate_science_acc_8.dat'):
        cate = line.strip('\n')
        words.append(cate_ins[cate])
    del cate_ins
    words = set(words)

    flag = False
    result = []
    with open("../result/science_words.dat",'a') as f:
        for line in open('./loreInstanceList.ttl'):
            if not line.startswith('<'):
                continue
            _type = line[line.index('>')+1:]
            _type = t.split(':')[0]
            title = line[line.index('"')+1:line.rindex('"')]
            if _type == "enwiki" and title in words:
                result = []
                result.append(title)
                flag = True
            if not _type == "enwiki" and flag and len(result) == 1:
                result.append(title)
                flag = False
                f.write("\t".join(result))
                f.flush()
        

get_science_words()

