from catchers import Facebook

fb = Facebook()

def response(context, flow):
    saved = fb.catch(flow)
    if fb.match(flow) and saved == 0:
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
