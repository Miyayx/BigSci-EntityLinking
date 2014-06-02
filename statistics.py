#/usr/bin/python2.7
#encoding=utf-8

def multi_entities():
    count = 0
    for line in open():
        items = line.split("::;")
        if len(items) > 2:
            count += 1
    print "num of mention that has multi entities:",count

def longtest_title():
    length = 0
    for line in open():
        title = 
        if len(title) > length:
            length = len(title)

    print "length of the longest title:",length

def average_entities():
    num = 0.0
    _sum = 0.0
    for line in open():
        entities = line.strip("\n").strip("::;").split(":::")[1].split("::;")
        if len(entities) > 1:
            num += 1
            _sum += len(entities)
    print "average of entities of multi entities:",(_sum/num)


