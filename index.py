#/usr/bin/env/python.27
#encoding=utf-8

import os, sys

import lucene

from lucene import SimpleFSDirectory, System, File, Document, Field,StandardAnalyzer, IndexWriter, Version

DOCDIR   = "../../data/Mention2Entity.ttl"
INDEXDIR = "../../data/entity.index"

def luceneIndexer(docdir, indir):
    """
    IndexDocuments from a directory
    docdir:一个保存被索引文档的目录路径；
    indir :一个索引存储的目录路径。
    """
    lucene.initVN()
    indexdir= SimpleFSDirectory(File(INDEXIDR))
    analyzer= StandardAnalyzer(Version.LUCENE_30)
    index_writer= IndexWriter(indexdir, analyzer, True, IndexWriter.MaxFieldLength(512))

    for line in open():
        doc = Document()
        line = line.strip("\n").strip("\r").strip("::;")
        mention, entity = line.split(":::")
        doc.add(Field("mention", mention, Field.Store.YES, Field.Index.ANALYZED))
        doc.add(Field("entity", entity)

    index_writer.optimize()
    index_writer.close()

class LuceneRetriver:
    def __init__(self, indexdir):
        lucene.initVM()
        indir= SimpleFSDirectory(File(indexdir))
        lucene_analyzer= StandardAnalyzer(Version.LUCENE_30)
        lucene_searcher= IndexSearcher(indir)

    def retrive(self, query):

        my_query= QueryParser(Version.LUCENE_30,"mention",lucene_analyzer).parse(query)
        MAX= 10
        total_hits =lucene_searcher.search(my_query,MAX)
        print"Hits: ",total_hits.totalHits
        for hit in total_hits.scoreDocs:
            print"Hit Score: ",hit.score, "Hit Doc:",hit.doc, "HitString:",hit.toString()
            doc= lucene_searcher.doc(hit.doc)
            print doc.get("entity")

if __name__=="__main__":
    luceneIndexer(DOCDIR,INDEXDIR)
    lr = LuceneRetriver(INDEXDIR)
    lr.retrive("Beijing")


