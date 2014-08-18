
#!/usr/bin/python
#-*-coding:utf-8-*-

from db import MySQLDB
db = MySQLDB()
db.create_conn()
for line in open("./data/superPathIndex.dat"):
    c_uri, path = line.strip("\n").split("\t")
    db.insert_path(c_uri, path)
db.close()


