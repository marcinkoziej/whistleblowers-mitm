from pprint import pprint
import operator
import re
import urllib2
import json
from pymongo import MongoClient, TEXT
from types import MethodType

def catcher(f):
    f.is_catcher = True
    return f

class Catcher(object):
    mongo = None
    def __init__(self, hosts=None, paths=None, methods=None):
        self.hosts = hosts
        self.paths = paths
        self.methods = methods

        if Catcher.mongo is None:
            Catcher.mongo = MongoClient()
#            for fld in ['email', 'name', 'password', 'content','to_name','frm_name','nick']:
#                self.db.facts.create_index([(fld, TEXT)], sparse=True)

    @property 
    def db(self):
        return Catcher.mongo.whistleblowers

    @staticmethod
    def is_host(req, host):
        return re.search(host, req.host) != None

    @staticmethod
    def is_path(req, path):
        return re.search(path, req.path) != None

    @staticmethod
    def is_method(req, method):
        return req.method.upper() == method.upper()

    def is_content_type(self, req, content_type):
        con_type = req.headers['Content-Type']
        if con_type and con_type[0].startswith(content_type):
            return True
        return False


    def guess_post_data(self, req):
        content = req.get_decoded_content()
        if not content:
            return
        if self.is_content_type(req, 'application/json'):
            # facebook can put kind of trash before json data
            trash = "for (;;);"
            if content.startswith(trash):
                content = content[len(trash):]
            if content.startswith('{'):
                return JSONData(req)
            else:
                print "Not sure how to handle this jsons: %s" % content
                return
        else:
            # try to parse it as form data
            return PostData(req)


    def match(self, flow):
        req = flow.request
        
        def any_matches(pred, elems):
            return reduce(operator.or_, map(lambda x: pred(req, x), elems), False)

        if self.hosts is not None:
            if not any_matches(self.is_host, self.hosts):
                return False

        if self.paths is not None:
            if not any_matches(self.is_path, self.paths):
                return False

        if self.methods is not None:
            if not any_matches(self.is_method, self.methods):
                return False

        return True

    def catch(self, flow):
        if not self.match(flow): return None
        ctr = 0

        for funame in dir(self):
            f = getattr(self, funame)
            if type(f) == MethodType:
                try:
                    is_catcher = f.is_catcher
                except AttributeError:
                    is_catcher = False
                if is_catcher:
                    ctr += f(flow) or 0
        return ctr

    def save(self, flow, fact, selector=None):
        fact['server'] = flow.server_conn.address.host
        fact['client'] = flow.client_conn.address.host
        fact['timestamp_start'] = flow.request.timestamp_start
        fact['timestamp_end'] = flow.request.timestamp_end
        fact['host'] = flow.request.host
        fact['path'] = flow.request.path
        fact['method'] = flow.request.method
        
        if selector:
            fact_id = self.db.facts.upsert(selector, fact)
        else:
            fact_id = self.db.facts.insert(fact)
        return fact_id






def print_json(rr):
    try:
        pprint(fb_json(rr))
    except ValueError:
        print "cannot read JSON"
        pass

save = Catcher.save
# def save(fact):
#     pprint(fact)
#     with open("/tmp/{0}.log".format(fact['kind']), "a") as out:
#         pprint(fact, out)

def fb_json(resp):
    c = resp.get_decoded_content()
    trash1 = "for (;;);"
    if c.startswith(trash1):
        c = c[len(trash1):]
    try:
        return json.loads(c)
    except ValueError:
        return None


def form_data(rr):
    content = rr.get_decoded_content()
    return urllib2.urlparse.parse_qs(content, keep_blank_values=True)

fb_query = form_data


class PostData(object):
    def __init__(self, req, base_k=''):
        self.data = form_data(req)
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

class JSONData(object):
    def __init__(self, req, base_k=''):
        self.base_k = base_k
        content = req.get_decoded_content()
        self.data = json.loads(content)
    
    def val(self, *ks):
        v = self.data
        if self.base_k:
            v = v[self.base_k]
        for k in ks:
            v = v[k]
        return v






class GetData(object):
    def __init__(self, url):
        (self.scheme, self.netloc, self.path, self.params, self.query, self.anchor) = urllib2.urlparse.urlparse(url)
        self._data = None

    @property
    def data(self):
        if self._data is not None:
            return self._data
        self._data = urllib2.urlparse.parse_qs(self.query, keep_blank_values=1)
        return self._data


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

