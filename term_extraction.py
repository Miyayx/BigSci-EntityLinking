#/usr/bin/env python2.7
#-*-coding:utf-8-*-

LIMIT = 20
class TermExtractor:
    def __init__(self, ip="localhost", port=6060, timeout=20):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def get_terms(self, retry_times, instr):
        return self.get_limit_terms(retry_times, instr, LIMIT)

    def get_limit_terms(self, retry_times, instr, num):
        terms = []

        if retry_times <= 0:
            retry_times = 1

        success = False

        #Create a socket with a timeout
        while retry_times > 0 and not success:
            retry_times -= 1

            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            instr = "<cmd>\nnum="+str(num)+"\ntype=PhraseOnly\n</cmd>" + instr +"<end>\n"
            s.connect((self.ip, self.port))
            s.sendall(instr)
            result = s.recv(1024)
            terms = [r.split("\t")[0] for r in result.split("\n")]
            s.close()
            success = True

        print terms
        return terms

if __name__=="__main__":
    #i = 0
    #for s in open("../../data/abstract.txt"):
    #    s = s.strip("\n")
    #    if i > 5:
    #        break
    #    te = TermExtractor()
    #    te.get_terms(1,s)

    #    i += 1
    te = TermExtractor()
    te.get_terms(1,"John")

