#!/usr/bin/env/python2.7
#-*-coding:UTF-8-*-

import json

class QResult():

    def __init__(self, p, v, lan):
        self.prop        = p
        self.value       = v
        self.lang        = lan

    def __str__(self):
        return "%s: %s@%s"%(self.prop, self.value, self.lang)

    def __repr__(self):
        return json.dumps((self.__dict__), indent=2)
