
#!/usr/bin/env python
#-*-coding:utf-8-*-


def is_in_domain(self, c):
    """
    If c(uri) is in specific domain
    """
    domain = ['100271','104436','100262','103549','100301','104859','105485','109406','100269']
    uris = Xlore().get_type_uri(c)
    for u in uris:
        if u in domain:
            return True
        else:
            path = MySQLDB().get_superpath(u)
            if not path:
                continue
            for p in path.split("/"):
                if p in domain:
                    return True
    return False

def domain_constrain(self):
    """
    Filter the candidate list with domain
    """

    new_can = []
    for c in self.candidates:
        if self.is_in_domain(c):
            print c,"is in domain"
            new_can.append(c)

    self.candidates = new_can
    return new_can

