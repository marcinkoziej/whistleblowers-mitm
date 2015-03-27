
from catchers.base import *


class DuckDuckGo(Catcher):
    def __init__(self):
        hosts = [r".*duckduckgo\.com$"]
        super(DuckDuckGo, self).__init__(hosts)

    @catcher
    def query(self, flow):
        if filter(lambda x:flow.request.path.startswith(x), 
                  ['/t/nrjerr', '/ac/', '/s.js','/d.js']) != []:
            return 0
        gd = GetData(flow.request.path)
        if 'q' in gd.data:
            fact = {
                'query': gd.data['q'],
                'provider':'duckduckgo',
                'kind':'query'
            }
            self.save(flow, fact)
            return 1


class Google(Catcher):
    def __init__(self):
        hosts = [r"google\.[a-z]+$"]
        super(Google, self).__init__(hosts)

    @catcher
    def query(self, flow):
        gd = GetData(flow.request.path)
        if 'q' in gd.data:
            fact = {
                'query': gd.data['q'],
                'provider':'google',
                'kind':'query'
            }
            self.save(flow, fact)
            return 1
