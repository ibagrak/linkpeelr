import logging

from webapp2_extras import json

from google.appengine.api import urlfetch
from google.appengine.api import memcache

import settings
import common

import datetime

class RPCHandler(common.BaseAPIHandler):
    
    def get(self, action):
        logging.debug("get: %s" % str(action))
        args = self.request.GET
        
        for arg in args:
            args[arg] = self.request.get(arg)
        
        if not action in settings.APIS:
            self.prep_json_response(400, key = 'unsupported')
        else:    
            getattr(self, action)(args)

    def peel(self, args, orig_url = None):
        logging.debug("peel req: %s" % str(args))
        url = args['url']
        result = None
            
        try: 
            result = urlfetch.fetch(url, method = urlfetch.HEAD, follow_redirects = False, deadline = 1)
            code = result.status_code
            if code == 301 or code == 302:
                result = common.get_error(code, message = {'url' : result.headers['Location']})

                last = {'time'     : str(datetime.datetime.now()),
                        'unpeeled' : orig_url if orig_url else url, 
                        'peeled'   : result['response']['url'], 
                        'where'    : args['where'], 
                        'ip'       : args['ip'] }
                memcache.set(key = "last", value = last, time = 3600)  
            else:
                result = common.get_error(code)
            
            self.response.set_status(code)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.encode(result))
    
        except urlfetch.InvalidURLError:
            self.prep_json_response(404, key = 'dne')
        except urlfetch.DownloadError:
            self.prep_json_response(402, key = 'failed')
        except Exception as e:
            raise e

        return result

    def peel_all(self, args):
        logging.debug("peel all req: %s" % str(args))
        
        orig_url = args['url']
        last_good_result = result = self.peel(args, orig_url = orig_url)
        
        while (result['code'] == 301 or result['code'] == 302):
            last_good_result = result
            args['url'] = result['response']['url']
            result = self.peel(args, orig_url = orig_url)
            
        self.response.clear()
        self.response.set_status(last_good_result['code'])
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.encode(last_good_result))

        return last_good_result

    def last(self, args):
        logging.debug("last req: %s" % str(args))
        
        kvs = memcache.get("last")
        
        if kvs:
            self.prep_json_response(200, message = kvs)
        else:
            self.prep_json_response(402, key = 'failed')

class LegacyRPCHandler(RPCHandler):
    
    def get(self):
        pass

