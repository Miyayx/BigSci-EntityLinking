#!/usr/bin/python2.7
#-*-coding:UTF-8-*-

from utils import *
import MySQLdb

class AminerDB():

    def __init__(self):
        configs = ConfigTool.parse_config("db.cfg","QueryLog")
        print "configs:",configs
        self.host   = configs["host"]
        self.port   = int(configs["port"])
        self.user   = configs["user"]
        self.passwd = configs["password"]
        self.db     = 'aminer_db'
        self.table  = 'jconf'
        self.conn   = None
        try:
            self.conn=MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd,db=self.db,port=self.port)
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def get_conf(self):
        cur = self.conn.cursor()
        cur.execute('SELECT DISTINCT capitalname FROM %s;'%self.table)
        result = cur.fetchall()
        cur.close()

        for r in result:
            if not r[0]:
                continue
            for a in r[0].split("/"):
                print a

if __name__=="__main__":
    db = AminerDB()
    db.get_conf()
