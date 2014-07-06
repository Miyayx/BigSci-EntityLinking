#!/usr/bin/python
#-*-coding:utf-8-*-

from db import MySQLDB
db = MySQLDB()
for line in open("./data/all_authors.dat"):
    aus = line.strip("\n").split(",")
    if len(aus) == 1:
        continue
    aus.sort(lambda x,y:cmp(len(x),len(y)))
    #aus[-1] is full name
    cs = db.get_candidate_and_count(aus[-1])
    if len(cs) == 0: #if full name has no candidate, that means no such mention in db
        continue

    c_c = sorted(cs.iteritems(), key=lambda d:d[1], reverse = True)
    best = c_c[0][0]
    for a in aus[:-1]:
        if len(db.get_candidate_and_count(a)) == 0:
            # if this mention has no candidates, add its full name's candidates to db
            print "best:",best
            print "mention:",a
            db.insert_candidate(a,best,1)


