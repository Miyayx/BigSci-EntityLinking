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
    print "configs:",
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
PREFIX = "http://xlore.org"
#GRAPH = 'xlore2'

"""
Format 修改记录：
1. ch--> zh
2. delete super_topic
"""

QUERY_LABEL = {
#        "title"       :"label",
#        "abstract"    :"comment",
#        "type"        :"InstanceOf",
#        "related_item":"hasReferedTo",
#        "image"       :"hasImage",
#        "icon"        :"hasIcon",
        "title"       :"http://www.w3.org/2000/01/rdf-schema#label",
        "abstract"    :"http://www.w3.org/2000/01/rdf-schema#comment",
        "type"        :"http://www.w3.org/2002/07/owl#InstanceOf",
        "related_item":"http://xlore.org/property#hasReferedTo",
        "image"       :"http://xlore.org/property#hasImage",
        "icon"        :"http://xlore.org/property#hasIcon",
        "topclass"    :"http://xlore.org/property#hasTopClass"
        }

class Xlore():

    def __init__(self):
        configs = ConfigTool.parse_config("./config/db.cfg","XLore")
        print configs
        import sys
        if re.match('linux',sys.platform):#Linux
            #self.db = JenaVirtDB(**configs)
            self.db = OdbcVirtDB(**configs)
            #self.db = WrapperVirtDB(configs['host'], "8890")
        else:
            self.db = OdbcVirtDB(**configs)
            #self.db = WrapperVirtDB(configs['host'], "8890")
        self.GRAPH = configs['graph']

    def get_instance_properties(self, entity_id):
        sq = 'select * from <%s> where {<%s/instance/%s> ?p ?o}'%(self.GRAPH, PREFIX, entity_id)
        return self.db.query(sq)

    def get_concept_label(self, entity_id, lan=None):
        if 'en' == lan or 'zh' == lan:
            sq = 'select * from <%s> where {<%s/concept/%s> <%s> ?o FILTER(langMatches(lang(?o), "%s"))}'%(self.GRAPH, PREFIX, entity_id, QUERY_LABEL["title"], lan)
        else:
            sq = 'select * from <%s> where {<%s/concept/%s> <%s> ?o }'%(self.GRAPH, PREFIX, entity_id, QUERY_LABEL["title"])
        rs = self.db.query(sq)
        return self.parse_label(rs)
    
    def get_title(self, entity_id, lan=None):
        if 'en' == lan or 'zh' == lan:
            sq = 'select * from <%s> where {<%s/instance/%s> <%s> ?o FILTER(langMatches(lang(?o), "%s"))}'%(self.GRAPH, PREFIX, entity_id, QUERY_LABEL["title"], lan)
        else:
            sq = 'select * from <%s> where {<%s/instance/%s> <%s> ?o }'%(self.GRAPH, PREFIX, entity_id, QUERY_LABEL["title"])
        rs = self.db.query(sq)
        return self.parse_label(rs)

    def get_abstract(self, entity_id, lan=None):
        sq = 'select * from <%s> where {<%s/instance/%s> <%s> ?o }'%(self.GRAPH, PREFIX, entity_id, QUERY_LABEL["abstract"])
        rs = self.db.query(sq)
        return self.parse_abstract(rs, lan)

    def parse_label(self, results):
        d = dict((r.lang, r.value) for r in results)
        return d

    def parse_abstract(self, results, lan):
        d = {'en':'', 'zh':''}
        for r in results:
            if 'enwiki' == r.lang and not 'zh' == lan:
                d['en'] = r.value
            if 'baidu' == r.lang and not 'en' == lan:
                d['zh'] = r.value
                break
            if 'hudong' == r.lang and not 'en' == lan:
                d['zh'] = r.value
                break
            if 'zhwiki' == r.lang and not 'en' == lan:
                d['zh'] = r.value
                break
        return d

    def get_type_uri(self, entity_id):
        c_uri = []
        sq = 'select * from <%s> where {<%s/instance/%s> <%s> ?type }'%( self.GRAPH, PREFIX, entity_id, QUERY_LABEL["type"])
        qrs = self.db.query(sq)
        for r in qrs:
            c_e_id = r.value.split("/")[-1]
            c_uri.append(c_e_id)
        return c_uri

    def get_type(self, entity_id, lan="en"):
        sq = 'select * from <%s> where {<%s/instance/%s> <%s> ?type }'%(self.GRAPH, PREFIX, entity_id, QUERY_LABEL["type"])
        qrs = self.db.query(sq)
        results = []
        for r in qrs:
            c_e_id = r.value.split("/")[-1]
            label = self.get_concept_label(c_e_id)
            results.append(label)
        return results

    def get_title_and_image(self, uri, lan, n = 1):
        entity_id = uri.split('/')[-1]
        title = self.get_title(entity_id,lan)
        images = self.get_icon(entity_id)
        return {"uri":uri, "title": title, "image": images[0] if len(images) > 0 else ""}

    def get_icon(self, entity_id):
        sq = 'select * from <%s> where {<%s/instance/%s> <%s> ?o FILTER(!langMatches(lang(?o), "baidu"))}'%(self.GRAPH, PREFIX, entity_id, QUERY_LABEL["icon"])
        qrs = self.db.query(sq)
        return [qrs[0].value] if len(qrs) else []

    def get_images(self, entity_id, n = 3):
        image_urls = []
        sq = 'select * from <%s> where {<%s/instance/%s> <%s> ?o FILTER(!langMatches(lang(?o), "baidu"))}'%(self.GRAPH, PREFIX, entity_id, QUERY_LABEL["image"])
        qrs = self.db.query(sq)
        return [qr.value for qr in qrs[:n]]  

    def get_innerLink(self, entity_id):

        sq = 'select * from <%s> where { <%s/instance/%s> <%s> ?link}'%(self.GRAPH, PREFIX, entity_id, QUERY_LABEL["related_item"])
        return self.db.query(sq)


    def get_topclass_from_ins(self, e_id):
        """
        获得instance的topclass集合, 只有concept有topclass属性，所以instance的topclass是它所属的concept的topclass
        """
        r = set()
        uris = self.get_type_uri(e_id)
        for u in uris:
            tops = self.get_topclass_from_con(u)
            r.update(set(tops))
        return r

    def get_topclass_from_con(self, c_id):
        """
        获得concept的topclass集合, 通过sparql查询
        """
        c_uri = []
        sq = 'select * from <%s> where {<%s/concept/%s> <%s> ?tc }'%(self.GRAPH, PREFIX, c_id, QUERY_LABEL["topclass"])
        qrs = self.db.query(sq)
        for r in qrs:
            c_id = r.value.split("/")[-1]
            c_uri.append(c_id)
        return c_uri

    def get_littleentity(self, entity_id, lan):
        """
        Get little entity according to entity_id
        """
        entity = {}
        entity["uri"] = os.path.join(os.path.join(PREFIX,'instance'),entity_id)
        entity["url"] = os.path.join(XLORE_URL_PREFIX+os.path.join(PREFIX,'instance'),entity_id)

        entity["title"] = self.get_title(entity_id, lan)
        entity["type"] = self.get_type(entity_id, lan)
        entity["abstract"] = self.get_abstract(entity_id, lan)
        #entity["image"] = self.get_image(entity_id)
        entity["image"] = self.get_icon(entity_id)
        return entity

    def create_littleentity(self, entity_id, lan):
            
        entity = {}
        entity_id = str(entity_id)
        entity["uri"] = os.path.join(os.path.join(PREFIX, 'instance'),entity_id)
        entity["url"] = os.path.join(os.path.join(XLORE_URL_PREFIX,os.path.join(PREFIX, 'instance')), entity_id)

        print "entity_id", entity_id

        qrs = self.get_instance_properties(entity_id)

        d = {}
        for qr in qrs:
            d[qr.prop] = d.get(qr.prop,[]) + [qr]

        result = {}
        #print d[QUERY_LABEL['abstract']]

        print d
        entity["title"] = self.parse_label(d[QUERY_LABEL['title']])
        entity["type"] = [self.get_concept_label(c.value.split("/")[-1], lan) for c in d.get(QUERY_LABEL['type'],[]) ] if QUERY_LABEL["type"] in d else []
        r_items = d.get(QUERY_LABEL['related_item'], [])
        #print r_items
        r_items = sorted(r_items, key=lambda x:int(x.value.split('/')[-1]))
        entity["related_item"] = [self.get_title_and_image(i.value, lan) for i in r_items[:20]] 
        entity["abstract"] = self.parse_abstract(d[QUERY_LABEL['abstract']], lan) if QUERY_LABEL["abstract"] in d else {}
        entity["image"] = [d[QUERY_LABEL["icon"]][0].value] if QUERY_LABEL["icon"] in d else [] 
        return entity


if __name__=="__main__":
    #db = DB()
    #db.get_candidateset("country")
    #db.has_mention("protocal")

    xlore = Xlore()
   # print xlore.get_images(3)
   # print xlore.get_icon(3)
   # print xlore.get_abstract(3)
   # print xlore.get_title(3)
   # print xlore.get_innerLink(1039711)
   # print xlore.get_type(2,"all")
   # print xlore.get_littleentity("2","all")
    result = xlore.create_littleentity(3,"all")
    print json.dumps(result, indent=2)
    
    #print xlore.db.query('select * from <xlore2> where {<http://xlore.org/instance/2> ?p ?type }')
