#!/usr/bin/env python2.7
#encoding=utf-8

import urllib
import urllib2
import xml.etree.cElementTree as ET
import codecs

from bs4 import BeautifulSoup

from utils import *

ENTITY_FILE = "entity.dat"
LINK_INFO   = "link.dat"

class Crawler:

    def __init__(self):
        pass

    def run(self):
        cat_url = 'http://www.wikicfp.com/cfp/allcat'
        html = urllib2.urlopen(cat_url).read()
        soup = BeautifulSoup(html)
        table = soup.find(class_="contsec").find("table").find("table")
        hrefs = table.findAll("a")
        catalogs = [h.text for h in hrefs]
        for c in catalogs:
            print c

class WikiGetter:
    def __init__(self):
        self.prefix = 'http://en.wikipedia.org/w/api.php'
        self.entities = set() 
        with open(LINK_INFO,"w") as f:
            f.write("")
        with open(ENTITY_FILE,"w") as f:
            f.write("")

    def get_page(self, l):
        for i in l:
            url = 'http://en.wikipedia.org/w/api.php?format=xml&action=query&titles=%s&prop=revisions&rvprop=content'%(i.replace(" ","%20"))
            data = urllib2.urlopen(url).read()
            yield data

    def more_item(self, generator):
        items = []
        for d in generator:
            parser = WikiParser(d)
            title = parser.parse_title()
            if not title:
                continue
            self.entities.add(title)
            print "title:",title
            #with open(title+".xml","w") as f:
            #    f.write(d)

            its = parser.find_entity(parser.parse_content())

            with codecs.open(LINK_INFO,"a", "utf-8") as f:
                f.write(title+"\t\t")
                for i in its:
                    f.write(i)
                    f.write(";;")
                f.write("\n")

            its = diff_items(its, self.entities) 
            items.extend(its)

        return items

    def get_init_items(self,fn):
        return [l.strip("\n") for l in open(fn)]

    def start(self, items):
        if len(self.entities) > 10000:
            return 
        items = self.more_item(self.get_page(items))
        self.start(items)

    def run(self):
        try:
           items = self.get_init_items('catalog.dat')
           self.entities.update(items)
           self.start(items)
        finally:
           write_lines(ENTITY_FILE, self.entities)

class WikiParser:
    def __init__(self, xml):
        self.root = ET.fromstring(xml)

    def find_entity(self, text):
        items = set()
        import re
        #pattern = re.compile('\[\[\w+\]\]')
        #print pattern.search(text).group()
        for item in re.findall('\[\[.+?\]\]',text):
            item = item[2:-2]
            if len(item.split("|")) == 2:
                item = item.split("|")[0]
            elif len(item.split("|")) > 2:
                continue
            if item.startswith("#"): # 井号要怎么办
                item = item[1:]
            #print "item:",item
            items.add(item)
        return list(items)

    def parse_content(self):
        try:
            if len(self.root[0]) == 1:
                return None
            else:
                content =  self.root[0][1][0][0][0].text
            end = content.rfind("== In fiction ==")
            end = end if end > -1 else content.find("\n\n== References ==\n\n")
            content = content[:end]
            return content
        except Exception,e:
            return None

    def parse_title(self):
        if len(self.root[0]) == 1:
            print "Error:",self.root[0][0][0].attrib["title"]
            return None
        else:
            return self.root[0][1][0].attrib["title"]



if __name__ =="__main__":
    #c = Crawler()
    #c.run()
    w = WikiGetter()
    w.run()

