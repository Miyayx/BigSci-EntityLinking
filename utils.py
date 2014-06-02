#/usr/bin/python2.7
#encoding=utf-8
import codecs

def common_items(a,b):
    """
    Find the common element of the two lists
    Will change the sequence
    """
    return list(set(a) & set(b))

def diff_items(a,b):
    """
    Find the different element between the two lists
    Will change the sequence
    """
    return list(set(a)^ set(b))

def write_lines(fn,lines):
    with codecs.open(fn,"w") as f:
        for l in lines:
            f.write(l+"\n")
    

