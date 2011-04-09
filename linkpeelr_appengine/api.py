'''
Created on 26.9.2010

@author: ibagrak
'''
__author__ = "Ilya Bagrak <ilya.bagrak@gmail.com>"

import logging

from django.utils import simplejson

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch

import settings


logger = logging.getLogger('api')
logger.setLevel(logging.DEBUG)

class Peeled(db.Model):
    updated = db.DateTimeProperty(auto_now = True)
    unpeeled = db.URLProperty(required = True)
    peeled = db.URLProperty(required = True)
    
    where = db.StringProperty(required = True)
    ip = db.StringProperty(required = True)

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
        
    def peel(self, kvs):
        logger.debug("peel req: %s" % str(kvs))
        url = kvs['url']
        store_last = False
        result = {}
        
        if 'version' in kvs and (kvs['version'] > "1.7"):
            store_last = True
            
        try: 
            result = urlfetch.fetch(url, method = urlfetch.HEAD, follow_redirects = False, deadline = 1)
            code = result.status_code
            if code == 301 or code == 302:
                result = (int(code), result.headers['Location'])
                
                if store_last:
                    entity = db.Query(Peeled).get()
                    if entity:
                        entity.unpeeled = url
                        entity.peeled = result[1]
                        entity.where = kvs['where']
                        entity.ip = kvs['ip']
                    else:
                        entity = Peeled(unpeeled = url, peeled = result[1], where = kvs['where'], ip = kvs['ip'])
                
                    entity.put()
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
        
        last_good_result = result = self.peel(kvs)
        
        while (result[0] == 301 or result[0] == 302):
            last_good_result = result
            kvs['url'] = result[1]
            result = self.peel(kvs)
            
        return last_good_result

    def last(self, kvs):
        logger.debug("last req: %s" % str(kvs))
        entity = db.Query(Peeled).get()
        
        if entity:
            return (settings.OK, [str(entity.updated), entity.unpeeled, entity.peeled, entity.where, entity.ip])
        else:
            return (settings.GENERAL_ERROR)
        
def main():
    logger = logging.getLogger('api')
    logger.setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/api', APIHandler)], debug=False)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()