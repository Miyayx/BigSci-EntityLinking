#!/usr/bin/env/python2.7
#-*-coding:UTF-8-*-

class LittleEntity():

    def __init__(self, _id, uri, url,type, title, super_topic, abstract, image, similarity = 0):
        self._id        = _id
        self.uri        = uri
        self.url        = url
        self.type     = type
        self.title    = title
        self.super_topic = super_topic
        self.abstract = abstract
        self.image    = image
        self.sim      = similarity

    def __str__(self):
        return "title:"+str(self.title)+"#"+"uri:"+str(self.uri)+"image_url:"+str(self.image)




