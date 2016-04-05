#!/usr/bin/env/python2.7
#-*-coding:UTF-8-*-

import json

class SearchItem():

    def __init__(self, uri, url, type, title, abstract, image):
        self.uri      = uri
        self.type     = type
        self.label    = title
        self.abstract = abstract
        self.depiction   = image
        self.resource    = uri

    def __str__(self):
        return "label:"+str(self.label)+"#"+"uri:"+str(self.uri)+"image_url:"+str(self.depiction)

    def __repr__(self):
        return str(self.__dict__)
