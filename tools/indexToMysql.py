#!/usr/bin/python
#-*-coding:utf-8-*-

from ConfigParser import ConfigParser
import MySQLdb 

class ConfigTool():
    @staticmethod
    def parse_config(fn, section):
        cf = ConfigParser()
        cf.read(fn)
        return dict(cf.items(section))

class TitleURIdb():

    configs = ConfigTool.parse_config("../db.cfg","MySQL")
    print "configs:",configs
    HOST   = configs["host"]
    PORT   = int(configs["port"])
    USER   = configs["user"]
    PASSWD = configs["password"]
    DBNAME = 'entity_linking'
    _db = None
    try:
        _db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD,db=DBNAME,port=PORT,charset='utf8')
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def __init__(self):
        self.table = 'title_uri'
        self.conn  = TitleURIdb._db

    def create_new_table(self, table):
        """
        CREATE  TABLE `entity_linking`.`title_uri` (
        `id` INT NOT NULL AUTO_INCREMENT ,
        `title` VARCHAR(2000) NOT NULL ,
        `uri` VARCHAR(45) NOT NULL ,
        PRIMARY KEY (`id`) ,
        UNIQUE INDEX `id_UNIQUE` (`id` ASC) ,
        UNIQUE INDEX `uri_UNIQUE` (`uri` ASC) ,
        UNIQUE INDEX `title_UNIQUE` (`title` ASC) 
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """

        self.table = table
        drop_str = "DROP TABLE IF EXISTS %s;"%(table)
        create_str = """
        CREATE  TABLE %s.%s (
        id INT NOT NULL AUTO_INCREMENT ,
        title VARCHAR(2000) NOT NULL ,
        uri VARCHAR(45) NOT NULL ,
        PRIMARY KEY (id) ,
        UNIQUE INDEX id_UNIQUE (id ASC) ,
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """%(TitleURIdb.DBNAME, table)
        
        cur = self.conn.cursor()
        cur.execute(drop_str)
        self.conn.commit()
        cur.execute(create_str)
        self.conn.commit()
        
        cur.close()
    
    def index_to_mysql(self):
        cur = self.conn.cursor()
        title = None
        uri   = None
        #for line in open("../data/loreInstanceList.ttl"):
        for line in open("/home/xlore/rdfdb/loreInstanceList.ttl"):
            if not line.startswith("<"):
                continue
            u = line[(line.index('<')+1):line.index('>')]
            t = line[(line.index('"')+1):line.rindex('"')]
            if t == title:
                continue
            else:
                uri = u
                title = t
                u = MySQLdb.escape_string(u)
                t = MySQLdb.escape_string(t)
                insert_str = "INSERT INTO %s (title,uri) VALUES('%s','%s');"%( self.table, t, u)
                print insert_str
                try: 
                    cur.execute(insert_str)
                    self.conn.commit()
                except Exception,e:
                    pass
                
        cur.close()

if __name__=="__main__":
    db = TitleURIdb()
    db.create_new_table("title_uri")
    db.index_to_mysql()

