#!/usr/bin/env/python2.7
#-*-coding:UTF-8-*-

class LittleEntity():

    def __init__(self, uri, title, abstract, image, similarity = 0):
        self.entity_uri = uri
        self.title    = title
        self.abstract = abstract
        self.image    = image
        self.sim      = similarity

    def __str__(self):
        return "title:"+str(self.title)+"#"+"uri:"+str(self.entity_uri)+"image_url:"+str(self.image_url)




