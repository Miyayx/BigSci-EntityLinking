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

def querylog_staticstic(fn):
    for line in open(fin):
        items = line.split("\t")
        if items[4] == "[Click] Search":
            keywords.add(items[3])
    

def staticstic(fn):
    pass


def search_keyword_statistics(fn):
    confs = [line.strip("\n").upper() for line in open("data/conference.dat")]
    conf_count = 0
    import nltk
    for k in open(fn):
        k = k.strip("\n")
        if len(k.split())==1:
            #if len(k) > 2 and len(k) < 7 and k.isupper():
            if k.upper() in confs: 
                print "Coference",k
                conf_count += 1
                continue
        text = nltk.word_tokenize(k)
        tags = [tag for word, tag in nltk.pos_tag(text)]
        nnp = tags.count('NNP')
        nn = tags.count('NN')
        #if nnp+nn == len(tags) and len(k) < 15:
        #    print "Name",k
        #elif len(tags) > 3:
        #    print "Paper",k
    print "Conf Count:",conf_count

        
        
from utils import *
import MySQLdb

class QueryLogDB():

    def __init__(self):
        configs = ConfigTool.parse_config("db.cfg","QueryLog")
        print "configs:",configs
        self.host   = configs["host"]
        self.port   = int(configs["port"])
        self.user   = configs["user"]
        self.passwd = configs["password"]
        self.db     = 'aminer_log'
        self.table  = 'logrecord_2012'
        self.conn   = None
        try:
            self.conn=MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd,db=self.db,port=self.port)
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def get_types(self):
        cur = self.conn.cursor()
        cur.execute('SELECT DISTINCT operation FROM '+self.table)
        result = cur.fetchall()
        cur.close()

        types = [r[0] for r in result]
        return types

    def count_type(self, t):
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(operation) FROM '+self.table+' WHERE operation="'+t+'"')
        result = cur.fetchone()
        cur.close()
        return result[0]

    def get_keyword_from_type(self, t):
        cur = self.conn.cursor()
        cur.execute('SELECT keyword FROM '+self.table+' WHERE operation="'+t+'"')
        result = cur.fetchall()
        cur.close()
        keywords = [r[0] for r in result]
        return set(keywords)


if __name__=="__main__":
    #search_info("../../zjt/querylog/querylog2012.txt","data/query_keywords.dat")
    #querylog = QueryLogDB()
    #types = querylog.get_types()
    #print types
    #for t in types:
    #    print t,querylog.count_type(t)
    #write_lines("./data/query_keywords.dat",querylog.get_keyword_from_type(types[1]))

    search_keyword_statistics("./data/query_keywords.dat")

