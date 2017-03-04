'''
Created on Sep 23, 2010

@author: ibagrak
'''
__author__ = "Ilya Bagrak <ilya.bagrak@gmail.com>"

import os
import webapp2
import jinja2
import logging

import api

logger = logging.getLogger('index')
logger.setLevel(logging.DEBUG)

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(webapp2.RequestHandler):
    
  def get(self):
    template = jinja_environment.get_template('index.html') 
    self.response.write(template.render({}))
              
app = webapp2.WSGIApplication([('/', MainPage), ('/api', api.APIHandler)], debug = True)

"""
def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
"""