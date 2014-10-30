#!/usr/bin/env python
#-*-coding:utf-8-*-

"""
Reference: http://textminingonline.com/how-to-use-stanford-named-entity-recognizer-ner-in-python-nltk-and-other-programming-languages
Luckily, NLTK provided an interface of Stanford NER: A module for interfacing with the Stanford taggers. The example use Stanford NER in Python with NLTK like the following:

    >>> from nltk.tag.stanford import NERTagger
    >>> st = NERTagger(‘/usr/share/stanford-ner/classifiers/all.3class.distsim.crf.ser.gz’,
            … ‘/usr/share/stanford-ner/stanford-ner.jar’)
    >>> st.tag(‘Rami Eid is studying at Stony Brook University in NY’.split())
    [('Rami', 'PERSON'), ('Eid', 'PERSON'), ('is', 'O'), ('studying', 'O'),
            ('at', 'O'), ('Stony', 'ORGANIZATION'), ('Brook', 'ORGANIZATION'),
            ('University', 'ORGANIZATION'), ('in', 'O'), ('NY', 'LOCATION')]
"""

import os

from nltk.tag.stanford import NERTagger
STANFORD_PATH = os.path.join(os.path.dirname(__file__),'stanford-ner')

class Parser(object):
    def __init__(self):
        self.st = NERTagger(os.path.join(STANFORD_PATH,'classifiers/english.all.3class.distsim.crf.ser.gz'), os.path.join(STANFORD_PATH,'stanford-ner-3.4.jar'))

    def NER(self, s):
        s = s.replace('.',' ')
        s = s.encode('utf-8')
        return self.st.tag(s.split())

if __name__ == "__main__":
    p = Parser()
    #print p.NER("I went to New York to meet John Smith")
    #print p.NER("Michael Jordan")
    for line in open('data/news.txt'):
        print p.NER(line)


