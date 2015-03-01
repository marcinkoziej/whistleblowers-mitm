from pprint import pprint
import operator
import re
import urllib2
import json

def catcher(f):
    f.is_catcher = True
    return f

class Catcher(object):
    def __init__(self, host, *paths):
        self.host = host
        self.paths = paths

    @staticmethod
    def is_host(req, host):
        return re.search(host, req.host) != None

    @staticmethod
    def is_path(req, path):
        return re.search(path, req.path) != None

    def match(self, flow):
        q = flow.request
        if not self.is_host(q, self.host): return False
        if not reduce(operator.or_, map(lambda x: self.is_path(q, x),self.paths), False): return False
        return True


    def catch(self, flow):
        if not self.match(flow): return
        ctr = 0

        for funame in dir(self):
            f = getattr(self, funame)
            try:
                is_catcher = f.is_catcher
            except AttributeError:
                is_catcher = False
            if is_catcher:
                ctr += f(flow) or 0

def fb_query(rr):
    return urllib2.urlparse.parse_qs(rr.get_decoded_content())

def print_json(rr):
    try:
        pprint(fb_json(rr))
    except ValueError:
        print "cannot read JSON"
        pass


def save(fact):
    print "FACT!!"
    pprint(fact)
    with open("/tmp/fb.log","a") as out:
        pprint(fact, out)


def fb_json(resp):
    c = resp.get_decoded_content()
    trash1 = "for (;;);"
    if c.startswith(trash1):
        c = c[len(trash1):]
    try:
        return json.loads(c)
    except ValueError:
        return None


class PostData(object):
    def __init__(self, req, base_k=''):
        self.data = fb_query(req)
        self.base_k = base_k

    def key(self,*ks):
        if self.base_k:
            bk = self.base_k
        else:
            bk = ks[0]
            ks = ks[1:]
        return bk + ''.join(map(lambda x: "[{0}]".format(x), ks))

    def val(self,*ks):
        k = self.key(*ks)
        if k in self.data:
            return self.data[k][0]
        return None


def select(hsh, *path, **cond):
    c = hsh
    for p in path:
        if p in c:
            c = c[p]
        else:
            return None
    def matches(o, cond):
        for k,v in cond.items():
            if not (k in o and o[k] == v):
                return False
        return True

    if isinstance(c, list):
        return filter(lambda x: matches(x, cond), c)
    else:
        if matches(c, cond): 
            return c
        return None


def clean_fbid(fbid):
    if fbid.startswith('fbid:'):
        return int(fbid[5:])
    return fbid

