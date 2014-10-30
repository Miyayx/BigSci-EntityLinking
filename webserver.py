#!/usr/bin/env/python2.7
#-*-coding:UTF-8-*-

from twisted.web.resource import Resource
from twisted.web import server, resource, http
from twisted.web.static import File

import datetime
import json

from abstract_el import AbstractEL
from query_el import QueryEL
from bigsci_el import BigSciEL
import stanford_parser 
from db import *
from model.little_entity import LittleEntity

PREFIX = "http://keg.cs.tsinghua.edu.cn/instance/"

class EntityEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if isinstance(obj, LittleEntity):  
            return json.dumps(obj.__dict__, indent=2)
        return json.JSONEncoder.default(self, obj)  

class LinkingResource(Resource):

    def __init__(self, source):
        self.source = source

    def render_GET(self, request):
        request.setHeader("Access-Control-Allow-Origin","*")
        request.setHeader("Content-Type","application/json")
        
        return self.render_POST(request)

    def render_POST(self, request):
        request.setHeader("Access-Control-Allow-Origin","*")
        request.setHeader("Content-Type","application/json")

        args = dict((k,v[0]) for k,v in request.args.items())
        print "request args:",args
        if not args.has_key('type') or len(args['type']) == 0:
            args['type'] = 'query'
            
        if args['type'] == 'query':
            e = BigSciEL(args)
            e.set_candb(self.source["candb"])
            e.set_graph(self.source["graph"])
            e.run()
            data = {}
            data["query_str"] = e.query_str
            #data["entity"] = map(self.parse_query_result, e.entities)
            print "Queries:",len(e.queries)
            #data["entity"] = repr(e.queries[0].entities)
            es = [entity.__dict__ for entity in e.entities ]
            data["entity"] = es
            return json.dumps(data, indent=2)

        if args['type'] == 'abstract':
            e = AbstractEL(args)
            e.set_candb(self.source["candb"])
            e.set_graph(self.source["graph"])

            e.run()
            
            data = {}
            if args.has_key('paper_id'):
                data["paper_id"] = args["paper_id"] 
            data["text"] = e.text
            data["limit"] = 1
            qs = [query.d() for query in e.queries]
            data["queries"] = qs

            return json.dumps(data, indent=2)

        if args['type'] == 'el':
            e = QueryEL(args)
            e.set_candb(self.source["candb"])
            e.set_graph(self.source["graph"])
            e.set_en_parser(self.source["en_parser"])
            e.run()
            qs = [query.d() for query in e.queries]
            return json.dumps(qs,indent=2)

        else:
            #raise Exception
            print "NO Such type"

    def parse_result(self, q):
        query = {}
        query["query"] = q.text
        query["index"] = q.index
        query["entities"]  = map(self.parse_query_result, q.entities)

    def parse_abstract_result(self, q):
        query = {}
        query["query"] = q.text
        query["start"] = q.index
        query["entity_id"]  = q.entity_id
        query["entity_uri"] = q.entity_uri
        query["entity_url"] = q.entity_url
        return query

    def parse_entity_result(self, e ):
        entity = {}
        entity["entity_id"] = e._id
        entity["uri"]       = e.uri
        entity["url"]       = e.url
        entity["title"]     = e.title
        entity["type"]      = e.type
        entity["super_topic"]     = e.super_topic
        entity["related_item"]     = e.related_item
        entity["abstract"]  = e.abstract
        entity["image"]     = e.image
        return entity


class PageResource(Resource):
     
    def render_GET(self,request):
        request.setHeader("Access-Control-Allow-Origin","*")
        request.setHeader("Content-Type","application/json")
        return " Hello World!"

if __name__=="__main__":
    source = {
            "candb": MySQLDB(),
            "graph": Xlore(),
            "en_parser": stanford_parser.Parser()
            }
    root = Resource()
    #root.putChild("show", PageResource())
    root.putChild("show", File("./web_ui"))
    root.putChild("linking", LinkingResource(source))

    from twisted.internet import reactor

    reactor.listenTCP(5656, server.Site(root))
    try:
        reactor.run()
    except:
        print "excpet"
        reactor.stop()
        reactor.run()


