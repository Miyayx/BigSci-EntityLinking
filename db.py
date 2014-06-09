#!/usr/bin/python2.7
#-*-coding:UTF-8-*-

import MySQLdb

import urllib2
from urllib import quote
from bs4 import BeautifulSoup

class MySQLDB():

    def __init__(self):
        self.host   = '10.1.1.23'
        self.port   = 3306
        self.user   = 'zjt'
        self.passwd = 'zjt'
        self.db     = 'entity_linking'
        self.table  = 'mention2entities'
        self.conn   = None
        try:
            self.conn=MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd,db=self.db,port=self.port)
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def get_candidateset(self, mention):
        cur = self.conn.cursor()
        cur.execute('SELECT entity FROM '+self.table+' WHERE mention = "'+mention+'"')
        result = cur.fetchone()
        cur.close()
        if result:
            result = [r[r.index('<')+1:r.index('>')] for r in result]
            return result
        else:
            return None

    def get_mentions(self):
        cur = self.conn.cursor()
        cur.execute(' SELECT mention FROM '+self.table)
        cur.close()

    def has_mention(self,mention):
        cur = self.conn.cursor()
        cur.execute('SELECT entity FROM '+self.table+' WHERE mention = "'+mention+'"')
        #if cur.fetchone()
        cur.close()

    def close(self):
        self.conn.close()



class Xlore():

    def __init__(self):
        pass

    @staticmethod
    def get_abstract(entity_id):
        sq = 'select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s>  <http://keg.cs.tsinghua.edu.cn/property/enwiki/abstract> ?object }'%entity_id
        URL = 'http://xlore.org/sparql.action' 
        page = unicode(urllib2.urlopen(URL+"?sq="+quote(sq)).read(),'utf-8')
        soup = BeautifulSoup(page)
        table = soup.find("table")
        if len(table.findAll("tr")) == 1:
            return None
        else:
            abstract = table.findAll("tr")[1].find("td").text.encode('utf-8')
            return abstract

    @staticmethod
    def get_fulltext(entity_id):
        sq = 'select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s> <http://keg.cs.tsinghua.edu.cn/property/enwiki/fulltext> ?e}'%entity_id
        URL = 'http://xlore.org/sparql.action' 
        page = urllib2.urlopen(URL+"?sq="+quote(sq)).read()
        soup = BeautifulSoup(page)
        table = soup.find("table")
        if len(table.findAll("tr")) == 1:
            return None
        else:
            fulltext = table.findAll("tr")[1].find("td").text
            return fulltext

    @staticmethod
    def get_littleentity(self, entity_id):
        entity = {}
        entity["uri"] = entity_id
        sq = ''
        URL = 'http://xlore.org/sparql.action' 
        page = unicode(urllib2.urlopen(URL+"?sq="+quote(sq)).read(),'utf-8')
        soup = BeautifulSoup(page)
        table = soup.find("table")
        if len(table.findAll("tr")) == 1:
            return None
        else:
            fulltext = table.findAll("tr")[1].find("td").text
            return entity


if __name__=="__main__":
    #db = DB()
    #db.get_candidateset("country")
    #db.get_mentions()
    #db.has_mention("protocal")

    xlore = Xlore()
    xlore.get_fulltext(1032938)
    
        


