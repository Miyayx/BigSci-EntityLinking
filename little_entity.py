#!/usr/bin/env/python2.7
#-*-coding:UTF-8-*-

class LittleEntity():

    def __init__(self, uri, title, abstract, pic, similarity = 0):
        self.entity_uri = uri
        self.title    = title
        self.abstract = abstract
        self.pic_url  = pic
        self.sim      = similarity



