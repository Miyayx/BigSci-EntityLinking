#!/usr/bin/env/python2.7
#encoding=utf-8

def convert(fn,newfn):
    count = 0
    with open(fn) as fr:
        with open(newfn,"w") as fw: 
            line = fr.readline()
            while line:
                count += 1
                if count % 10000 == 0:
                    print count
                if not line.startswith("<"):
                    line = fr.readline()
                    continue
                if "enwiki:label" in line:
                    line = fr.readline()
                    continue
                else:
                    id_ = line[(line.index('<')+1):line.index('>')]
                    label = line[(line.index('"')+1):line.rindex('"')]
                    fw.write("%s\t\t%s\n"%(label,id_))
                line = fr.readline()

def title_uri():
    with open("../BigSci-EntityLinking/data/loreEnwikiTitleID.dat","w") as f:
        for line in open("../BigSci-EntityLinking/data/loreEnwikiTitleURI.dat"):
            t,u = line.strip("\n").split("\t\t")
            u = u.split("/")[-1]
            f.write(t+"\t"+u+"\n")
            f.flush()

def inst_index(fin, fout):
    insts = set()
    for line in open(fin):
        line = line.strip("\n")
        insts.add(line)
    f = open(fout,"w")
    for i in insts:
        title,uri = i.split("\t\t")
        f.write("<"+uri+">\t\t"+title+"\n")
        f.flush()
    f.close()

if __name__=="__main__":
    convert("./data/loreInstanceList.ttl","./data/loreChTitleID.dat")
    #title_uri()
    inst_index("./data/loreChTitleID.dat","./data/chInstIndx.ttl")
    
    
