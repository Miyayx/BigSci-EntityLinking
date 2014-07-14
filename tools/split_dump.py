#!/usr/bin/python
#-*-coding:utf-8-*-

P_NUM = 300000

def split_dump(in_dir, out_dir, dump_f):
    start_num = 0
    end_num   = 0
    n = 1
    fn = out_dir+dump_f.split(".")[0]+"{:0>2d}.xml-p{:0>10d}p{:0>10d}".format(n, start_num, start_num+P_NUM)
    f = open(fn,"w")
    for l in open(in_dir+dump_f):
        if l.startswith("<mediawiki"): # article start
            if end_num % P_NUM == 0:
                f.close()
                n += 1
                fn = out_dir+dump_f.split(".")[0]+"{:0>2d}.xml-p{:0>10d}p{:0>10d}".format(n,start_num,end_num)
                start_num = end_num 
                f = open(fn,"w")
        if l.startswith("</mediawiki>"): # article end
            end_num += 1

        f.write(l)
        f.flush()
    f.close()

if __name__=="__main__":
    import os 
    for f in os.listdir("/home/zigo/sy/etc/dump/"):
        split_dump("/home/zigo/sy/etc/dump/","/home/zjt/enwikiMap/data/new-wiki-article/",f)
