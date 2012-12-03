'''
Created on Sep 23, 2010

@author: ibagrak
'''
__author__ = "Ilya Bagrak <ilya.bagrak@gmail.com>"

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '0.96')

import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import api

class MainPage(webapp.RequestHandler):
    
    def get(self, *args):
        path = os.path.join(os.path.dirname(__file__), "index.html")     
        self.response.out.write(template.render(path, {}))
              
application = webapp.WSGIApplication([
                                      ('/',                 MainPage),
                                     ], debug = True)

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
