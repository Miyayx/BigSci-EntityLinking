#!/usr/bin/python2.7
#-*-coding:UTF-8-*-

import MySQLdb
import pyodbc
from bs4 import BeautifulSoup

import urllib2
from urllib import quote

from utils import *

XLORE_URL="http://xlore.org/sigInfo.action"
XLORE_URL_PREFIX="http://xlore.org/sigInfo.action?uri="
PREFIX = "http://keg.cs.tsinghua.edu.cn/instance/"

class MySQLDB():

    def __init__(self):
        configs = ConfigTool.parse_config("db.cfg","MySQL")
        print "configs:",configs
        self.host   = configs["host"]
        self.port   = int(configs["port"])
        self.user   = configs["user"]
        self.passwd = configs["password"]
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
        result = cur.fetchall()
        cur.close()
        print result[0]
        if result:
            result = [r[0][r[0].index('<')+1:r[0].index('>')] for r in result]
            return result
        else:
            return []

    def get_fuzzy_candidateset(self, mention):
        """
        untested
        """
        cur = self.conn.cursor()
        cur.execute('SELECT entity FROM '+self.table+' WHERE mention = "%'+mention+'%"')
        result = cur.fetchall()
        cur.close()
        if result:
            result = [r[0][r[0].index('<')+1:r[0].index('>')] for r in result]
            return result
        else:
            return None

    def get_mentions(self):
        cur = self.conn.cursor()
        cur.execute('SELECT DISTINCT mention FROM '+self.table)
        #for r in cur.fetchall():
        #    print r

        result = [r[0] for r in cur.fetchall()]
        cur.close()
        return result

    def has_mention(self,mention):
        cur = self.conn.cursor()
        cur.execute('SELECT entity FROM '+self.table+' WHERE mention = "'+mention+'"')
        #if cur.fetchone()
        cur.close()

    def get_link_count(self, mention, entity):
        cur = self.conn.cursor()
        cur.execute('SELECT count FROM '+self.table+' WHERE mention = "'+mention+'" AND entity = "'+ entity + '"')
        r = cur.fetchone()[0]
        cur.close()
        return r

    def get_all_link_count(self, mention):
        cur = self.conn.cursor()
        cur.execute('SELECT entity,count FROM '+self.table+' WHERE mention = "'+mention+'"')
        r = dict(cur.fetchall())
        cur.close()
        return r

    def close(self):
        self.conn.close()


class Xlore():

    configs = ConfigTool.parse_config("db.cfg","Xlore")
    print "configs:",configs
    HOST = configs["host"]
    PORT = int(configs["port"])
    UID  = configs["user"]
    PWD  = configs["password"]
    DRIVER = configs["driver"]
    #_virtodb = pyodbc.connect('DRIVER={VOS};HOST=%s:%d;UID=%s;PWD=%s'%(HOST, PORT, UID, PWD))
    _virtodb = pyodbc.connect('DRIVER=%s;HOST=%s:%d;UID=%s;PWD=%s'%(DRIVER, HOST, PORT, UID, PWD))
    
    def __new__(cls, *args, **kwargs):
        print "__new__"
        if not cls._virtodb:
            cls._virtodb = super(Xlore, cls).__new__(cls, *args, **kwargs)
        return cls._virtodb

    def __init__(self):
        #Xlore._virtodb = pyodbc.connect('DRIVER=/usr/lib64/virtodbc_r.so;HOST=%s:%d;UID=%s;PWD=%s')%(Xlore.HOST, Xlore.PORT, Xlore.UID, Xlore.PWD)
        pass

    def fetch_one_result(self, sq):
        """
        Fetch one result from xlore virtuoso database according to query the sq string

        return:
            one result(if hits) or None(if no hit)
        """
        cursor = Xlore._virtodb.cursor()
        results = cursor.execute(sq)
        try:
            result = results.fetchone()[0]
            if type(result) == tuple:
                print "result is tuple"
                result = result[0]
        except TypeError,e:
            return None
        finally:
            cursor.close()
        return result

    def fetch_multi_result(self, sq):
        """
        Fetch multi results from xlore virtuoso database according to query the sq string

        return:
            result list(if hits) or empty list(if no hit)
        """
        cursor = Xlore._virtodb.cursor()
        try:
            results = [r[0] for r in cursor.execute(sq).fetchall()]
            if results and len(results) > 0 and type(results[0]) == tuple:
                print "result is tuple"
                results = [r[0] for r in results]
        except TypeError,e:
            return []
        finally:
            cursor.close()
        return results

    def get_abstract(self, entity_id, lan="en"):
        if lan == "en":
            return {"en":self.get_en_abstract(entity_id)}
        if lan == "ch":
            return {"ch":self.get_ch_abstract(entity_id)}
        if lan == "all":
            return {"en":self.get_en_abstract(entity_id),"ch":self.get_ch_abstract(entity_id)}

    def get_en_abstract(self, entity_id):
        sq = 'sparql select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s>  <http://keg.cs.tsinghua.edu.cn/property/enwiki/abstract> ?object }'%entity_id
        return self.fetch_one_result(sq)

    def get_ch_abstract(self, entity_id):
        ch_baike = ["zhwiki", "baidu", "hudong"]
        for ch in ch_baike:
            sq = 'sparql select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s> <http://keg.cs.tsinghua.edu.cn/property/%s/abstract> ?title}'%(entity_id,ch)
            result = self.fetch_one_result(sq)
            if result:
                return result
        return None

    def get_title(self, entity_id, lan="en"):
        if lan == "en":
            return {"en":self.get_en_title(entity_id)}
        if lan == "ch":
            return {"ch":self.get_ch_title(entity_id)}
        if lan == "all":
            return {"en":self.get_en_title(entity_id),"ch":self.get_ch_title(entity_id)}

    def get_en_title(self, entity_id):
        sq = 'sparql select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s> <http://keg.cs.tsinghua.edu.cn/property/enwiki/label> ?title}'%entity_id
        return self.fetch_one_result(sq)

    def get_ch_title(self, entity_id):
        ch_baike = ["zhwiki", "baidu", "hudong"]
        for ch in ch_baike:
            sq = 'sparql select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s> <http://keg.cs.tsinghua.edu.cn/property/%s/label> ?title}'%(entity_id,ch)
            result = self.fetch_one_result(sq)
            if result:
                return result
        return None

    def get_fulltext(self, entity_id, lan="en"):
        if lan == "en":
            return {"en":self.get_en_fulltext(entity_id)}
        if lan == "ch":
            return {"ch":self.get_ch_fulltext(entity_id)}
        if lan == "all":
            return {"en":self.get_en_fulltext(entity_id),"ch":self.get_ch_fulltext(entity_id)}

    def get_en_fulltext(self, entity_id):
        sq = 'sparql select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s>  <http://keg.cs.tsinghua.edu.cn/property/enwiki/fulltext> ?object }'%entity_id
        return self.fetch_one_result(sq)

    def get_ch_fulltext(self, entity_id):
        ch_baike = ["zhwiki", "baidu", "hudong"]
        for ch in ch_baike:
            sq = 'sparql select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s> <http://keg.cs.tsinghua.edu.cn/property/%s/fulltext> ?e}'%(entity_id,ch)
            result = self.fetch_one_result(sq)
            if result:
                return result
        return None

    def get_image(self, entity_id, n = 3):
        image_urls = []
        lore = ["enwiki","baidu","hudong","zhwiki"]
        for l in lore:
            sq = 'sparql select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s> <http://keg.cs.tsinghua.edu.cn/property/%s/image> ?img }'%(entity_id, l)
            image_urls += self.fetch_multi_result(sq)
            if len(image_urls) > n:
                break
        return image_urls[:n] if len(image_urls) >= 3 else image_urls

    def get_innerLink(self, entity_id):

        sq = 'sparql select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s>  <http://keg.cs.tsinghua.edu.cn/property/enwiki/fulltext> ?object }'%entity_id
        return self.fetch_multi_result(sq)

    def get_littleentity(self, entity_id, lan):
        entity = {}
        entity["_id"] = entity_id
        entity["uri"] = PREFIX+entity_id
        entity["url"] = XLORE_URL_PREFIX+PREFIX+entity_id

        #cursor = Xlore._virtodb.cursor()
        #sq = 'sparql select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s> <http://keg.cs.tsinghua.edu.cn/property/enwiki/label> ?title}'%entity_id
        #entity["title"] = cursor.execute(sq).fetchone()[0][0]

        #sq = 'sparql select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s>  <http://keg.cs.tsinghua.edu.cn/property/enwiki/abstract> ?object }'%entity_id
        #a = cursor.execute(sq).fetchone()
        #entity["abstract"] = a[0][0] if a else None

        entity["title"] = self.get_title(entity_id, lan)
        entity["abstract"] = self.get_abstract(entity_id, lan)
        entity["image"] = self.get_image(entity_id)
        print "entity", entity
        return entity

    @staticmethod
    def get_abstract_from_web(entity_id):
        URL = 'http://xlore.org/sparql.action' 
        sq = 'select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s>  <http://keg.cs.tsinghua.edu.cn/property/enwiki/abstract> ?object }'%entity_id
        try:
            page = unicode(urllib2.urlopen(URL+"?sq="+quote(sq)).read(),'utf-8')
        except:
            page = unicode(urllib2.urlopen(URL+"?sq="+quote(sq)).read(),'utf-8')
        soup = BeautifulSoup(page)
        table = soup.find("table")
        if len(table.findAll("tr")) == 1:
            return None
        else:
            abstract = table.findAll("tr")[1].find("td").text.encode('utf-8')
            return abstract

    @staticmethod
    def get_fulltext_from_web(entity_id):
        URL = 'http://xlore.org/sparql.action' 
        sq = 'select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s> <http://keg.cs.tsinghua.edu.cn/property/enwiki/fulltext> ?e}'%entity_id
        page = urllib2.urlopen(URL+"?sq="+quote(sq)).read()
        soup = BeautifulSoup(page)
        table = soup.find("table")
        if len(table.findAll("tr")) == 1:
            return None
        else:
            fulltext = table.findAll("tr")[1].find("td").text
            return fulltext

    @staticmethod
    def get_littleentity_from_web(entity_id):
        print entity_id
        entity = {}
        entity["uri"] = entity_id
        #URL = 'http://xlore.org/sparql.action' 
        #sq = 'select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s> <http://keg.cs.tsinghua.edu.cn/property/enwiki/label> ?title; <http://keg.cs.tsinghua.edu.cn/property/enwiki/abstract> ?abstract}'%entity_id
        #page = unicode(urllib2.urlopen(URL+"?sq="+quote(sq)).read(),'utf-8')
        #soup = BeautifulSoup(page)
        #table = soup.find("table")
        #if len(table.findAll("tr")) == 1:
        #    return None
        #else:
        #    tds = table.findAll("tr")[1].findAll("td")
        #    entity["title"]    = tds[0].text
        #    entity["abstract"] = tds[1].text
        #    images = Xlore.get_image(entity_id)
        #    entity["image"] = images[0] if len(images) > 0 else None
        #    return entity

        entity["title"]    = Xlore.get_title(entity_id)
        entity["abstract"] = Xlore.get_abstract(entity_id)
        images = Xlore.get_image(entity_id)
        entity["image"] = images[0] if len(images) > 0 else None
        return entity

    @staticmethod
    def get_image_from_web(entity_id):
        image_urls = []
        lore = ["enwiki","baidu","hudong","zhwiki"]
        URL = 'http://xlore.org/sparql.action' 
        for l in lore:
            sq = 'select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s> <http://keg.cs.tsinghua.edu.cn/property/%s/image> ?img }'%(entity_id, l)
            try:
                page = unicode(urllib2.urlopen(URL+"?sq="+quote(sq)).read(),'utf-8')
            except:
                page = unicode(urllib2.urlopen(URL+"?sq="+quote(sq)).read(),'utf-8')
            soup = BeautifulSoup(page)
            table = soup.find("table")
            if len(table.findAll("tr")) == 1:
                continue
            else:
                image_urls += [tr.find("td").text for tr in table.findAll("tr")[1:]]
                if len(image_urls) > 6:
                    return image_urls
        return image_urls

    @staticmethod
    def get_title_from_web(entity_id):
        sq = 'select * from <lore4> where{ <http://keg.cs.tsinghua.edu.cn/instance/%s> <http://keg.cs.tsinghua.edu.cn/property/enwiki/label> ?title}'%entity_id
        URL = 'http://xlore.org/sparql.action' 
        try:
            page = unicode(urllib2.urlopen(URL+"?sq="+quote(sq)).read(),'utf-8')
        except:
            page = unicode(urllib2.urlopen(URL+"?sq="+quote(sq)).read(),'utf-8')
        soup = BeautifulSoup(page)
        table = soup.find("table")
        if len(table.findAll("tr")) == 1:
            return None
        else:
            title = table.findAll("tr")[1].find("td").text
            return title
        

if __name__=="__main__":
    #db = DB()
    #db.get_candidateset("country")
    #db.get_mentions()
    #db.has_mention("protocal")

    xlore = Xlore()
    #print xlore.get_image(1032938)
    #print xlore.get_abstract(1032938)
    #print xlore.get_fulltext(1032938)
    print xlore.get_title(6612130)
    #print xlore.get_littleentity(1032938)
    
