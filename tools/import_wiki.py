#!/usr/bin/python
#-*-coding:utf-8-*-

from nltk.corpus import stopwords
from ../db.py import *

def get_outof_xlore_list(fold, fnew):
    olds = [line.strip("\n") for line in open(fold)]
    news = [line.strip("\n") for line in open(fnew)]
    return list(set(news)-set(olds))

if __name__=="__main__":
    ws = get_outof_xlore_list("/home/zigo/sy/etc/enwiki-title.dat","/home/lsj/data/enwiki/enwiki-instance")
    print len(ws)


