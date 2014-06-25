#!/usr/bin/python2.7
#-*-coding:UTF-8-*-


def search_info(fin, fout):
    keywords = set()
    for line in open(fin):
        items = line.split("\t")
        if items[4] == "[Click] Search":
            keywords.add(items[3])

    with open(fout,"w") as f:
        for k in keywords:
            f.write(k+"\n")
        

#types = [line.split("\t")[4] for line in open("../../zjt/querylog/querylog2012.txt")]
#for t in set(types):
#    print t

if __name__=="__main__":
    search_info("../../zjt/querylog/querylog2012.txt","data/query_keywords.dat")


