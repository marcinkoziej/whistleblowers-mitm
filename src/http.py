from pprint import pprint
from catchers import *

catchers = [ \
             Facebook(), Twitter(),\
             Gmail(), Cahoots(),\
             DuckDuckGo(), Google(),\
             PostMethod(), ]
other_catcher = Get()

def response(context, flow):
    saved = 0
    for c in catchers:
        saved += c.catch(flow) or 0
    if saved == 0:
        saved += other_catcher.catch(flow) or 0

    if saved is None:
        q = flow.request
        print "---> ", q.method, q.host, q.path
        if q.method == "POST" and q.content:
            print "--[ POST:"
            pprint(form_data(q))
            print "--[ RETURN:"
        print_json(flow.response)
