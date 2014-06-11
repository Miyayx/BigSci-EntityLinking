#!/usr/bin/env/python2.7
#-*-coding:UTF-8-*-

from twisted.web.resource import Resource
from twisted.web import server, resource, http

import datetime
import simplejson

from entity_linking import AbstractEL
from entity_linking import QueryEL
from db import *

class LinkingResource(Resource):
    def render_GET(self, request):
        return 'get'
    def render_POST(self, request):
        args = dict((k,v[0]) for k,v in request.args.items())
        print "request args:",args
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
            e = QueryEL(args)
            data = {}
            data["query_str"] = e.query_str
            data["entity"] = map(self.parse_query_result, e.entities)
            return simplejson.dumps(data)
        else:
            #raise Exception
            print "NO Such type"
        return 'post'

    def parse_abstract_result(self, q):
        query = {}
        query["query"] = q.text
        query["start"] = q.start
        query["end"]   = q.end
        query["entity_uri"] = q.entity_id
        query["similar"] = q.similarity 
        return query

    def parse_query_result(self, e ):
        entity = {}
        entity["title"] = e.title
        entity["abstract"] = e.abstract
        entity["image"]    = e.image
        entity["sim"]      = e.sim 
        return entity

if __name__=="__main__":
    root = Resource()
    root.putChild("linking", LinkingResource())

    from twisted.internet import reactor

    reactor.listenTCP(8880, server.Site(root))
    reactor.run()


