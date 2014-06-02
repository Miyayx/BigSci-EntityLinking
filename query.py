#/usr/bin/python2.7
#encoding=utf-8

class Query():

    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end

        self.entity_id = 0
        self.similarity = 0


        
