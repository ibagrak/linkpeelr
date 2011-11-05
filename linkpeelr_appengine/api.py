'''
Created on 26.9.2010

@author: ibagrak
'''
__author__ = "Ilya Bagrak <ilya.bagrak@gmail.com>"

import logging
import datetime

from django.utils import simplejson

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.api import memcache

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
        kvs['ip'] = self.request.remote_addr
        
        if not action in settings.APIS:
            result = (settings.INVALID_API_ERROR)
        else:    
            result = getattr(self, action)(kvs)
                
        logger.debug("JSON result %s" % simplejson.dumps(result))
        self.response.out.write(simplejson.dumps(result))
        
    def peel(self, kvs, orig_url = None):
        logger.debug("peel req: %s" % str(kvs))
        url = kvs['url']
        store_last = False
        result = {}
            
        try: 
            result = urlfetch.fetch(url, method = urlfetch.HEAD, follow_redirects = False, deadline = 1)
            code = result.status_code
            if code == 301 or code == 302:
                result = (int(code), result.headers['Location'])
                
                last = {'time'     : str(datetime.datetime.now()),
                        'unpeeled' : orig_url, 
                        'peeled'   : result[1], 
                        'where'    : kvs['where'], 
                        'ip'       : kvs['ip'] }
                memcache.set(key = "last", value = last, time = 3600)  
            else:
                result = (int(code), )
            
        except urlfetch.InvalidURLError:
            result = (settings.INVALID_URL_ERROR,)
        except urlfetch.DownloadError:
            result = (settings.DOWNLOAD_ERROR,)
        except:
            result = (settings.GENERAL_ERROR,)

        return result

    def peel_all(self, kvs):
        logger.debug("peel all req: %s" % str(kvs))
        
        orig_url = kvs['url']
        last_good_result = result = self.peel(kvs, orig_url = orig_url)
        
        while (result[0] == 301 or result[0] == 302):
            last_good_result = result
            kvs['url'] = result[1]
            result = self.peel(kvs, orig_url = orig_url)
            
        return last_good_result

    def last(self, kvs):
        logger.debug("last req: %s" % str(kvs))
        
        kvs = memcache.get("last")
        
        if kvs:
            return (settings.OK, [kvs['time'], kvs['unpeeled'], kvs['peeled'], kvs['where'], kvs['ip']])
        else:
            return (settings.GENERAL_ERROR)
        
def main():
    logger = logging.getLogger('api')
    logger.setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/api', APIHandler)], debug=False)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
