#!/usr/bin/python2.7
#-*-coding:UTF-8-*-

import MySQLdb
import pyodbc
from bs4 import BeautifulSoup

import urllib2
from urllib import quote

from utils import *
from virtdb import *


class MySQLDB():

    configs = ConfigTool.parse_config("./config/db.cfg","MySQL")
    print "configs:",configs
    HOST   = configs["host"]
    PORT   = int(configs["port"])
    USER   = configs["user"]
    PASSWD = configs["password"]
    DBNAME = configs["db"]

    def __init__(self):
        #configs = ConfigTool.parse_config("db.cfg","MySQL")
        #print "configs:",configs
        #self.host   = configs["host"]
        #self.port   = int(configs["port"])
        #self.user   = configs["user"]
        #self.passwd = configs["password"]
        #self.db     = 'entity_linking'
        self.table  = MySQLDB.configs["table"]
        self.conn   = None
        #try:
        #    self.conn=MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd,db=self.db,port=self.port)
        #except MySQLdb.Error, e:
        #    print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def create_conn(self):
        if self.conn:
            self.conn.close()
        try:
            self.conn = MySQLdb.connect(host=MySQLDB.HOST, user=MySQLDB.USER, passwd=MySQLDB.PASSWD,db=MySQLDB.DBNAME,port=MySQLDB.PORT, charset="utf8")
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def get_candidateset(self, mention):
        self.create_conn()

        cur = self.conn.cursor()
        q = 'SELECT entity FROM '+self.table+' WHERE mention = "'+MySQLdb.escape_string(mention)+'"'
        print q
        cur.execute(q)
        result = cur.fetchall()
        cur.close()
        del cur
        if result:
            result = [r[0] for r in result]
            return result
        else:
            return []

    def get_candidate_and_count(self, mention):
        self.create_conn()

        cur = self.conn.cursor()
        cur.execute('SELECT entity,count FROM '+self.table+' WHERE mention = "'+MySQLdb.escape_string(mention)+'"')
        result = cur.fetchall()
        cur.close()
        del cur
        if result:
            result = dict((r[0],r[1]) for r in result)
            return result
        else:
            return {}

    def has_mention(self,mention):
        self.create_conn()

        cur = self.conn.cursor()
        cur.execute('SELECT entity FROM '+self.table+' WHERE mention = "'+mention+'"')
        cur.close()
        del cur

    def get_link_count(self, mention, entity):
        self.create_conn()

        cur = self.conn.cursor()
        cur.execute('SELECT count FROM '+self.table+' WHERE mention = "'+mention+'" AND entity = "'+ entity + '"')
        r = cur.fetchone()[0]
        cur.close()
        del cur
        return r

    def get_all_link_count(self, mention):
        self.create_conn()

        cur = self.conn.cursor()
        cur.execute('SELECT entity,count FROM '+self.table+' WHERE mention = "'+mention+'"')
        r = dict(cur.fetchall())
        cur.close()
        del cur
        return r

    def get_littleentity(self, title):
        self.create_conn()

        entity = {}
        entity["_id"] = ""
        entity["uri"] = ""
        entity["url"] = "http://en.wikipedia.org/wiki/"+"_".join(title.split())

        cur = self.conn.cursor()
        cur.execute('SELECT type,super_topic,abstract,image FROM wiki_db WHERE title= "'+MySQLdb.escape_string(title)+'"')
        result = cur.fetchone()
        cur.close()
        del cur

        if not result:
            return None

        entity["title"] = {"en":title,"ch":""}
        if result[0]:
            entity["type"] = [{"en":r,"ch":""} for r in result[0].split(";")]
        else:
            entity["type"] = []
        if result[1]:
            entity["super_topic"] = [{"en":r,"ch":""} for r in result[1].split(";")]
        else:
            entity["super_topic"] = []
        entity["abstract"] = {"en":result[2] if result[2] else "","ch":""}
        entity["image"] = []
        entity["related_item"] = []

        return entity

    def insert_wiki_entity(self, title, super_topic, abstract,url):
        self.create_conn()

        cur = self.conn.cursor()
        title = MySQLdb.escape_string(title)
        url = MySQLdb.escape_string(url)
        super_topic = MySQLdb.escape_string(super_topic)
        abstract = MySQLdb.escape_string(abstract)
        cur.execute('INSERT INTO entity_linking.wiki_db (title,abstract,super_topic,url) VALUES("%s","%s","%s","%s");'%(title,abstract,super_topic,url))
        MySQLDB._db.commit()
        
        cur.close()

    def insert_candidate(self, mention, uri, count):
        self.create_conn()
        cur = self.conn.cursor()
        cur.execute('INSERT INTO %s (mention,entity,count) VALUES("%s","%s","%d");'%(self.table,mention,uri,count))
        MySQLDB._db.commit()
        cur.close()

    def insert_path(self, uri, path):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO %s (concept_uri,path) VALUES("%s","%s");'%("super_path",uri,path))
        self.conn.commit()
        cur.close()

    def close(self):
        if self.conn:
            self.conn.close()

    def get_superpath(self, c_uri):
        self.create_conn()
        cur = self.conn.cursor()
        print "super_path, uri =",c_uri
        cur.execute('SELECT path FROM '+'super_path'+' WHERE concept_uri = '+c_uri)
        result = cur.fetchone()
        cur.close()
        del cur
        return result[0] if result else None

XLORE_URL="http://xlore.org/sigInfo.action"
XLORE_URL_PREFIX="http://xlore.org/sigInfo.action?uri="
PREFIX = "http://keg.cs.tsinghua.edu.cn"
GRAPH = 'lore4'

class Xlore():

    
    def __init__(self):
        configs = ConfigTool.parse_config("./config/db.cfg","XLore")
        import sys
        if re.match('linux',sys.platform):#Linux
            #self.db = JenaVirtDB(**configs)
            self.db = OdbcVirtDB(**configs)
        else:
            self.db = OdbcVirtDB(**configs)
        GRAPH = configs['graph']

    def get_instance_properties(self, entity_id):
        sq = 'select * from <%s> where {<%s/instance/%s> ?p ?o}'%(GRAPH, PREFIX, entity_id)
        result_set = self.db.query(sq)
        result = {}
        for p, o in result_set:
            result[p] = result.get(p,[]) + [o]
        return result

    def get_concept_properties(self, entity_id):
        sq = 'select * from <%s> where {<%s/concept/%s> ?p ?o}'%(GRAPH, PREFIX, entity_id)
        result_set = self.db.query(sq)
        result = {}
        for p, o in result_set:
            result[p] = result.get(p,[]) + [o]
        return result

    def parse_properties(self, p2o):
        d = {}
        for p,o in p2o.items():
            items = p.split("/")
            if len(items) == 5: # no enwiki,zhwiki...
                d[items[-1]] = o
            if len(items) == 6:
                if not d.has_key(items[-1]):
                    d[items[-1]] = {}
                d[items[-1]][items[-2]] = o
        
        result = {}

        ch_baike = ["zhwiki","baidu","hudong"]
        
        for k,v in d.items():
            if isinstance(v, dict):
                if k == "abstract" or k == "label":
                    result[k] = {"en":v["enwiki"][0] if v.has_key("enwiki") else "", "ch":""}
                    for ch in ch_baike:
                        if v.has_key(ch):
                            import re
                            rs = [r'\(.*?:\s*?\)',r'（.*?：\s*?）',r'(\s*?)',r'（\s*?）',r'（.*?,\s*?）',r'（.*?，\s*?）'] 
                            for r in rs:
                                v[ch][0] = re.sub(r,"",v[ch][0])
                            result[k]["ch"] = v[ch][0]
                            break
                elif k == "image":
                    result[k] = v.get("enwiki",[]) + v.get("zhwiki",[]) + v.get("hudong",[])
                else:
                    s_ch = set()
                    for ch in ch_baike:
                        for i in v.get(ch,[]):
                            if i.startswith("http"):
                                s_ch.add(i)
                    s_en = set()
                    for i in v.get("enwiki",[]):
                        s_en.add(i)
                    result[k] = {"en":list(s_en) if v.has_key("enwiki") else [], "ch": list(s_ch)}
            else:
                result[k] = v

        return result

    def get_concept_label(self, entity_id, lan):
        if lan == "en":
            return {"en":self.get_en_concept_label(entity_id)}
        if lan == "ch":
            return {"ch":self.get_ch_concept_label(entity_id)}
        if lan == "all":
            return {"en":self.get_en_concept_label(entity_id),"ch":self.get_ch_concept_label(entity_id)}
    
    def get_en_concept_label(self, entity_id):
        sq = 'select * from <%s> where {<%s/concept/%s> <%s/property/enwiki/label> ?label}'%(GRAPH, PREFIX, entity_id, PREFIX)
        return self.db.fetch_one_result(sq)

    def get_ch_concept_label(self, entity_id):
        ch_baike = ["zhwiki", "baidu", "hudong"]
        for ch in ch_baike:
            sq = 'select * from <%s> where {<%s/concept/%s> <%s/property/%s/label> ?label}'%(GRAPH, PREFIX, entity_id, PREFIX, ch)
            result = self.db.fetch_one_result(sq)
            if result:
                return result
        return ""

    def get_abstract(self, entity_id, lan="en"):
        if lan == "en":
            return {"en":self.get_en_abstract(entity_id)}
        if lan == "ch":
            return {"ch":self.get_ch_abstract(entity_id)}
        if lan == "all":
            return {"en":self.get_en_abstract(entity_id),"ch":self.get_ch_abstract(entity_id)}

    def get_en_abstract(self, entity_id):
        sq = 'select * from <%s> where {<%s/instance/%s> <%s/property/enwiki/abstract> ?o }'%(GRAPH, PREFIX, entity_id, PREFIX)
        return self.db.fetch_one_result(sq)

    def get_ch_abstract(self, entity_id):
        ch_baike = ["zhwiki", "baidu", "hudong"]
        for ch in ch_baike:
            sq = 'select * from <%s> where {<%s/instance/%s> <%s/property/%s/abstract> ?title}'%(GRAPH, PREFIX, entity_id, PREFIX, ch)
            result = self.db.fetch_one_result(sq)
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
        sq = 'select * from <%s> where {<%s/instance/%s> <%s/property/enwiki/label> ?title}'%(GRAPH, PREFIX, entity_id, PREFIX)
        return self.db.fetch_one_result(sq)

    def get_ch_title(self, entity_id):
        ch_baike = ["zhwiki", "baidu", "hudong"]
        for ch in ch_baike:
            sq = 'select * from <%s> where {<%s/instance/%s> <%s/property/%s/label> ?title}'%(GRAPH, PREFIX, entity_id, PREFIX, ch)
            result = self.db.fetch_one_result(sq)
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
        sq = 'select * from <%s> where {<%s/instance/%s> <%s/property/enwiki/fulltext> ?object }'%(GRAPH, PREFIX, entity_id, PREFIX)
        return self.db.fetch_one_result(sq)

    def get_ch_fulltext(self, entity_id):
        ch_baike = ["zhwiki", "baidu", "hudong"]
        for ch in ch_baike:
            sq = 'select * from <%s> where { <%s/instance/%s> <%s/property/%s/fulltext> ?e}'%(GRAPH, PREFIX, entity_id, PREFIX, ch)
            result = self.db.fetch_one_result(sq)
            if result:
                return result
        return None

    def get_type_uri(self, entity_id):
        c_uri = []
        sq = 'select * from <%s> where {<%s/instance/%s> <%s/property/instanceOf> ?type }'%( GRAPH, PREFIX, entity_id, PREFIX)
        result = self.db.fetch_multi_result(sq)
        for r in result:
            c_e_id = r.split("/")[-1]
            c_uri.append(c_e_id)
        return c_uri

    def get_type(self, entity_id, lan="en"):
        if lan == "en":
            return {"en":self.get_en_type(entity_id)}
        if lan == "ch":
            return {"ch":self.get_ch_type(entity_id)}
        if lan == "all":
            return {"en":self.get_en_type(entity_id),"ch":self.get_ch_type(entity_id)}

    def get_en_type(self, entity_id):
        concepts = []
        sq = 'select * from <%s> where {<%s/instance/%s> <%s/property/instanceOf> ?type }'%(GRAPH, PREFIX, entity_id, PREFIX)
        result = self.db.fetch_multi_result(sq)
        for r in result:
            c_e_id = r.split("/")[-1]
            label = self.get_en_concept_label(c_e_id)
            if label:
                concepts.append(label)
        return concepts

    def get_ch_type(self, entity_id):
        concepts = []
        sq = 'select * from <%s> where { <%s/instance/%s> <%s/property/instanceOf> ?type}'%(GRAPH, PREFIX, entity_id, PREFIX)
        result = (self.db.fetch_multi_result(sq))
        for r in result:
            c_e_id = r.split("/")[-1]
            label = self.get_ch_concept_label(c_e_id)
            if label:
                concepts.append(label)
        return concepts

    def get_superclass(self, entity_id, lan="en"):
        if lan == "en":
            return {"en":self.get_en_superclass(entity_id)}
        if lan == "ch":
            return {"ch":self.get_ch_superclass(entity_id)}
        if lan == "all":
            return {"en":self.get_en_superclass(entity_id),"ch":self.get_ch_superclass(entity_id)}

    def get_en_superclass(self, entity_id):
        concepts = []
        sq = 'select * from <%s> where { <%s/instance/%s> <%s/property/iSubTopicOf> ?t }'%(GRAPH, PREFIX, entity_id, PREFIX)
        result = self.db.fetch_multi_result(sq)
        for r in result:
            c_e_id = r.split("/")[-1]
            label = self.get_en_concept_label(c_e_id)
            if label:
                concepts.append(label)
        return concepts

    def get_ch_superclass(self, entity_id):
        concepts = []
        sq = 'select * from <%s> where { <%s/instance/%s> <%s/property/iSubTopicOf> ?t}'%(GRAPH, PREFIX, entity_id, PREFIX)
        result = self.db.fetch_multi_result(sq)
        for r in result:
            c_e_id = r.split("/")[-1]
            label = self.get_ch_concept_label(c_e_id)
            if label:
                concepts.append(label)
        return concepts

    def get_title_and_image(self, entity_id,lan, n = 1):
        title = self.get_title(entity_id,lan)
        images = self.get_image(entity_id, n)
        return {"title": title, "image": images[0] if len(images) > 0 else ""}

    def get_image(self, entity_id, n = 3):
        image_urls = []
        lore = ["enwiki","hudong","zhwiki"]
        for l in lore:
            sq = 'select * from <%s> where { <%s/instance/%s> <%s/property/%s/image> ?img }'%(GRAPH, PREFIX, entity_id, PREFIX, l)
            image_urls += self.db.fetch_multi_result(sq)
            if len(image_urls) > n:
                break
        return image_urls[:n] if len(image_urls) >= 3 else image_urls

    def get_innerLink(self, entity_id):

        sq = 'select * from <%s> where { <%s/instance/%s> <%s/property/enwiki/innerLink> ?link}'%(GRAPH, PREFIX, entity_id, PREFIX)
        return self.db.fetch_multi_result(sq)

    def get_littleentity(self, entity_id, lan):
        entity = {}
        entity["_id"] = entity_id
        entity["uri"] = os.path.join(PREFIX,entity_id)
        entity["url"] = XLORE_URL_PREFIX+PREFIX+entity_id

        entity["title"] = self.get_title(entity_id, lan)
        entity["type"] = self.get_type(entity_id, lan)
        entity["super_topic"] = self.get_superclass(entity_id, lan)
        entity["abstract"] = self.get_abstract(entity_id, lan)
        entity["image"] = self.get_image(entity_id)
        return entity

    def create_littleentity(self, entity_id, lan):
            
        entity = {}
        entity_id = str(entity_id)
        entity["_id"] = entity_id
        entity["uri"] = PREFIX+'/'+entity_id
        entity["url"] = XLORE_URL_PREFIX+PREFIX+'/'+entity_id

        q_result = self.get_instance_properties(entity_id)
        d = self.parse_properties(q_result)

        entity["title"] = d["label"]
        entity["type"] = [self.get_concept_label(c.split("/")[-1], lan) for c in d.get("instanceOf",[]) ]
        entity["super_topic"] = [self.get_concept_label(c.split("/")[-1], lan) for c in d.get("iSubTopicOf",[]) ]
        if d.has_key("relatedItem"):
            entity["related_item"] = [self.get_title_and_image(uri.split("/")[-1],"all") for uri in d["relatedItem"]["en"]]+[self.get_title_and_image(uri.split("/")[-1],"all") for uri in d["relatedItem"]["ch"]]
        else:
            entity["related_item"] = []
        if d.has_key("abstract"):
            entity["abstract"] = {"en":d["abstract"]["en"], "ch":d["abstract"]["ch"]}
        else:
            entity["abstract"] = {"en":"","ch":""}
        entity["image"] = d["image"][0:3] if d.has_key("image") else []
        return entity
        

if __name__=="__main__":
    #db = DB()
    #db.get_candidateset("country")
    #db.has_mention("protocal")

    xlore = Xlore()
    print xlore.get_image(1032938)
    print xlore.get_abstract(1032938)
    print xlore.get_fulltext(1032938)
    print xlore.get_title(6612130)
    print xlore.get_innerLink(1039711)
    print xlore.get_type(1039711,"all")
    print xlore.get_superclass(1039711,"all")
    xlore.create_littleentity(1022540,"all")
    xlore.create_littleentity(1074721,"all")
    xlore.create_littleentity(1022540,"all")
    xlore.create_littleentity(1756117,"all")
    
