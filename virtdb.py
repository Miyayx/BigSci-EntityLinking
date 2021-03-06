#!/usr/bin/env python
#-*-coding=utf-8-*-
import os
import sys
import re

import pyodbc
import codecs

if not re.match('linux',sys.platform):
    from jpype import *

import urllib 
import urllib2 
import json
import simplejson

from utils import *

class VirtDB(object):
    """
    """

    def __init__(self, uid, pwd, graph, dsn=None, driver=None, host=None, port=None):
        self.HOST = host
        self.PORT = port
        self.DSN = dsn 
        self.DRIVER = driver
        self.UID = uid 
        self.PWD = pwd 
        self.GRAPH = graph
        self.charset="UTF-8"

    def connect(self):
        raise NotImplementedError("Subclasses should implement this!")

    def query(self, sq):
        raise NotImplementedError("Subclasses should implement this!")

    def close(self):
        raise NotImplementedError("Subclasses should implement this!")

class HttpDB(VirtDB):
    def __init__(self, url, uid, pwd, graph, host, port, prefix, dsn, driver):
        VirtDB.__init__(self, uid, pwd, graph, dsn, driver, host, port)

        self.url = url
        self.prefix = prefix

    def connect(self):
        pass

    #def query(self, t, id_):
    def query(self, sq):
        """
        request args need:
        id_
        type
        prefix
        graph
        host
        port
        uid
        pwd
        """

        param = {
                #"id_":id_,
                #"type":t,
                "sq":sq,
                "prefix":self.prefix,
                "graph":self.GRAPH,
                "uid":self.UID,
                "pwd":self.PWD,
                "host":self.HOST,
                "port":self.PORT,
                "dsn":self.DSN,
                "driver":self.DRIVER
                }

        f = urllib2.urlopen(urllib2.Request(self.url, urllib.urlencode(param)))
        resp = f.read()
        return json.loads(resp)

    def close(self):
        pass


class OdbcVirtDB(VirtDB):
    """
    """

    def __init__(self, uid, pwd, graph, dsn=None, host=None, port=None, driver=None):
        VirtDB.__init__(self, uid, pwd, graph, dsn, driver, host, port)

        self.db = None

    def connect(self):
        try:
            if self.DSN:
                self.db = pyodbc.connect("DSN=%s;UID=%s;PWD=%s;charset=%s"%(self.DSN, self.UID, self.PWD, self.charset) )
        except Exception,e:
            print e
            if self.DRIVER:
                print "use driver"
                self.db = pyodbc.connect('DRIVER={%s};HOST=%s:%s;UID=%s;PWD=%s;charset=UTF-8'%(self.DRIVER, self.HOST, str(self.PORT), self.UID, self.PWD))
            else:
                raise ValueError("Need DSN or DRIVER&&HOST&&PORT")

    def fetch_one_result(self, sq):
        """
        Fetch one result from xlore virtuoso database according to query the sq string

        return:
            one result(if hits) or None(if no hit)
        """
        if not self.db:
            self.connect()
        sq = "sparql " + sq
        cursor = self.db.cursor()
        try:
            results = cursor.execute(sq)
            result = results.fetchone()[0]
            if type(result) == tuple:
                result = result[0]
        except TypeError,e:
            return None
        finally:
            cursor.close()
        return result

    def fetch_multi_results(self, sq):
        """
        Fetch multi results from xlore virtuoso database according to query the sq string

        return:
            result list(if hits) or empty list(if no hit)
        """

        if not self.db:
            self.connect()
        sq = "sparql " + sq
        cursor = self.db.cursor()
        #help(cursor)

        try:
            print cursor.execute(sq).fetchone()
            results = [r[0] for r in cursor.execute(sq).fetchall()]
            if results and len(results) > 0 and type(results[0]) == tuple:
                results = [r[0] for r in results]
        except TypeError, e:
            return []
        finally:
            cursor.close()
        return results

    def query(self, sq):

        if not self.db:
            self.connect()

        sq = "sparql " + sq
        print self.db
        cursor = self.db.cursor()
        print cursor
        print ("Query:%s"%sq)
        try:
            results = [(r[0][0], r[1][0]) for r in cursor.execute(sq).fetchall()]
            #if results and len(results) > 0 and type(results[0]) == tuple:
            #    results = [r[0] for r in results]
        except TypeError, e:
            return []
        finally:
            cursor.close()
        return results

    def close(self):
        self.db.close()


class JenaVirtDB(VirtDB):
    """
    """

    def __init__(self, uid, pwd, graph, host=None, port=None):
        if not host:
            raise ValueError("Need Value:HOST")
        if not port:
            raise ValueError("Need Value:PORT")
        VirtDB.__init__(self, uid, pwd, graph, host=host, port=port)

        #self.jvmpath = getDefaultJVMPath()
        #startJVM(self.jvmpath, "-ea", "-Djava.ext.dirs={0}".format(os.path.abspath('.')+"/java/"))
        startJVM("C:/Program Files/Java/jre7/bin/server/jvm.dll","-ea","-Djava.ext.dirs={0}".format(os.path.abspath('.')+"/java/"))
        print ("JVM Start")
        VtsDB = JClass('movie.MovieVirt')
        self.db = VtsDB(host, port, uid, pwd, graph)

    def connect(self):
        pass

    def query(self, sq):
        r_list = []
        result = self.db.query(sq)
        for r in result:
            r_list.append((r.getK(), r.getV()))
        return r_list

    def close(self):
        shutdownJVM()

import simplejson
from SPARQLWrapper import SPARQLWrapper, JSON
from model.queryresult import QResult

class WrapperVirtDB(VirtDB):

    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port

        self.db = None
        self.connect()

    def connect(self):
        print "connect"
        self.db = SPARQLWrapper("http://%s:%s/sparql"%(self.host, self.port))

    def query(self, sq):
        results = []
        self.db.setQuery("""%s"""%sq)
        s,p,o = sq[sq.index('{'):sq.index('}')].strip().split()[:3]
        p = p.strip()
        o = o.strip()
        if o.startswith('?'):
            o = o[1:]
        self.db.setReturnFormat(JSON)
        for result in self.db.query().convert()["results"]["bindings"]:
            #print json.dumps(result, indent=2)
            if p.startswith('?'): #如果查的是property和object
                prop = p[1:]
                q = QResult(result[prop]['value'], result[o]['value'], result[o].get('xml:lang',''))
                results.append(q)
            else: #如果指定property，查询object
                prop = p[1:-1]
                q = QResult(prop, result[o]['value'], result[o].get('xml:lang',''))
                results.append(q)

        return results

    def close(self):
        pass


if __name__ == "__main__":
    configs = ConfigTool.parse_config("./config/db.cfg","MovieKB")
    string = "select * where {<http://keg.tsinghua.edu.cn/movie/instance/" + str(11510446) + "> ?p"+" ?o}"

    #db = JenaVirtDB(**configs)
    #for r in db.query(string):
    #    print (r[0]+" "+r[1])

    configs["url"] = "http://localhost:5678/query"
    configs["prefix"] = 'http://keg.tsinghua.edu.cn/movie/'

    db = HttpDB(**configs)
    for r in db.query("instance","b10050542"):
        print (r[0]+" "+r[1])
        

    

