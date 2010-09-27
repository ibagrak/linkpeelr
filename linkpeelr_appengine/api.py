'''
Created on 26.9.2010

@author: ibagrak
'''
__author__ = "Ilya Bagrak <ilya.bagrak@gmail.com>"

#import os
import logging
import urllib2

from django.utils import simplejson

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

import settings

logger = logging.getLogger('api')
logger.setLevel(logging.DEBUG)

class APIHandler(webapp.RequestHandler):
    """ 
    Will handle JSON requests.
    """
    def get(self):
        action = self.request.get('action')
        args = self.request.arguments()
        args.remove('action')
        kvs = {}
        
        for arg in args:
            kvs[arg] = self.request.get(arg)
        
        if not action in settings.APIS:
            result = (settings.INVALID_API_ERROR)
        else:    
            result = getattr(self, action)(kvs)
                
        logger.debug("got result %s" % str(result))
        logger.debug("simplejson.dumps %s" % simplejson.dumps(result))
        self.response.out.write(simplejson.dumps(result))
        
    def peel(self, kvs):
        logging.debug("got a peel action w/ %s" % str(kvs))
        url = kvs["url"]
        result = {}
        
        try: 
            result = urlfetch.fetch(url, method = urlfetch.HEAD, follow_redirects = False, deadline = 1)
            code = result.status_code
            if code == 301 or code == 302:
                result = (int(code), result.headers['Location'])
            else:
                result = (int(code))
            
        except urlfetch.InvalidURLError:
            result = (settings.INVALID_URL_ERROR)
        except urlfetch.DownloadError:
            result = (settings.DOWNLOAD_ERROR)
        except:
            result = (settings.GENERAL_ERROR)
        
        return result

    def peel_all(self, kvs):
        pass
    
def main():
    logger = logging.getLogger('api')
    logger.setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/api', APIHandler)], debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()