#/usr/bin/python2.7
#encoding=utf-8

class Query():

    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end

        self.entity_id  = 0
        self.entity_uri = ""
        self.entity_url = ""
        self.similarity = 0

    def __str__(self):
        return "Query:::text:%s start:%d end:%d entity id:%s\n"%(self.text, self.start, self.end, self.entity_id)


        
