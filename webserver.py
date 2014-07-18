#!/usr/bin/env/python2.7
#-*-coding:UTF-8-*-

from twisted.web.resource import Resource
from twisted.web import server, resource, http

import datetime
import simplejson

from entity_linking import AbstractEL
from entity_linking import QueryEL
from db import *

PREFIX = "http://keg.cs.tsinghua.edu.cn/instance/"

class LinkingResource(Resource):

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
            
        if args['type'] == 'abstract':
            db = MySQLDB()
            e = AbstractEL(args)
            e.set_db(db)
            e.run()
            
            data = {}
            data["paper_id"] = args["paper_id"]
            data["text"] = e.origin
            data["entity"] = map(self.parse_abstract_result, e.queries)

            return simplejson.dumps(data)

        if args['type'] == 'query':
            db = MySQLDB()
            xlore = Xlore()
            e = QueryEL(args)
            e.set_db(db)
            e.set_xlore(xlore)
            e.run()
            data = {}
            data["query_str"] = e.query_str
            data["entity"] = map(self.parse_query_result, e.entities)
            return simplejson.dumps(data)
        else:
            #raise Exception
            print "NO Such type"

    def parse_abstract_result(self, q):
        query = {}
        query["query"] = q.text
        query["start"] = q.start
        query["end"]   = q.end
        query["entity_id"]  = q.entity_id
        query["entity_uri"] = q.entity_uri
        query["entity_url"] = q.entity_url
        query["similar"] = q.similarity 
        return query

    def parse_query_result(self, e ):
        entity = {}
        entity["entity_id"] = e._id
        entity["uri"]       = e.uri
        entity["url"]       = e.url
        entity["title"]     = e.title
        #entity["type"]      = e.type
        #entity["super_topic"]     = e.super_topic
        entity["abstract"]  = e.abstract
        entity["image"]     = e.image
        entity["sim"]       = e.sim 
        return entity

if __name__=="__main__":
    root = Resource()
    root.putChild("linking", LinkingResource())

    from twisted.internet import reactor

    reactor.listenTCP(5656, server.Site(root))
    reactor.run()


