import common

class Index(common.BaseHandler):
    
    def get(self):
        # demonstrates how session state can be changed        
        self.session_inc_pageviews()
        
        self.prep_html_response('index.html', {})
