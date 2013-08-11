import logging
import traceback
import sys

import webapp2
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
        logging.info("peel req: %s" % str(args))
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
                        'ip'       : self.request.remote_addr }
                memcache.set(key = "last", value = last, time = 3600) 
            else:
                result = common.get_error(code)
            
            self.response.set_status(200)
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
    
    def handle_exception(self, exception, debug_mode):
        # Log the error.
        logging.exception(exception)

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
        else:
            self.response.set_status(500)
            
        if debug_mode:
            lines = ''.join(traceback.format_exception(*sys.exc_info()))
        else:
            lines = None
            
        self.response.clear()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.encode((500, lines)))

    def get(self):
        logging.debug("legacy get")
        args = self.request.GET
        action = None
        response = None

        for arg in args:
            args[arg] = self.request.get(arg)
        
        if not 'action' in args or not args['action'] in settings.APIS:
            response = { 'code' : 400 }
        else:
            action = args['action']
            getattr(self, action)(args)
            # extract response and clear the body
            response = json.decode(self.response.body)
        
        self.response.clear()

        # old API expects 200 response code on all non-exceptional responses
        self.response.set_status(200)
        self.response.headers['Content-Type'] = 'application/json'

        if 'response' in response:
            if action == 'last' and len(response['response']) == 5:
                last = response['response']
                self.response.write(json.encode((settings.LEGACY_API_CODES[response['code']], [last['time'], last['unpeeled'], last['peeled'], last['where'], last['ip']])))
            elif 'url' in response['response']:
                self.response.write(json.encode((settings.LEGACY_API_CODES[response['code']], response['response']['url'])))
            else: 
                self.response.write(json.encode((settings.LEGACY_API_CODES[response['code']], )))
        else: 
            self.response.write(json.encode((settings.LEGACY_API_CODES[response['code']], )))
