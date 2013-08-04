import common

class Index(common.BaseHandler):
    
    def get(self):
        self.prep_html_response('index.html', {})
