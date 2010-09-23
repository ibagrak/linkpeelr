'''
Created on Sep 23, 2010

@author: ibagrak
'''
__author__ = "Ilya Bagrak <ilya.bagrak@gmail.com>"

import logging


from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
    
    def get(self, *args):
        pass
              
application = webapp.WSGIApplication([
                                      ('/',                                   MainPage),
                                     ], debug=True)

           
def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
