BigSci-EntityLinking
====================

EntityLinking part of BigSci

keg@Tsinghua

##Database
###MySQL
* Fedora:

        yum install MySQL-python

* Ubuntu:

        apt-get install libmysqlclient-dev python-dev
        pip install MySQL-python

###Virtuoso
* Fedora:

        yum install unixODBC unixODBC-devel
        pip install pyodbc 
        pip install rdflib

* Ubuntu:

        apt-get install unixODBC unixODBC-dev
        pip install pyodbc 
        pip install rdflib

Setting：

##Third-party package
* nltk 

        pip install nltk

> need nltk.download() to download nltk corpas

* bs4    
 
        pip install BeautifulSoup4

* twisted 

        pip install twisted

##Others
* Fedora

        yum install wine

* Ubuntu

        apt-get install wine

##Server Start Step
1. start term extractor

           wine termextracttools.exe   in term/bin/


2. start web server

           python webserver.py  in BigSci-EntityLinking/

##Test Demo
    python web_test.py
