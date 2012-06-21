import logging
import cgi
import sys
import traceback
import hashlib
import os
from functools import wraps

import webapp2
from webapp2_extras import sessions, json, auth
from jinja2.runtime import TemplateNotFound

import settings
import model
from handlers import jinja_environment

def get_json_error(code, key = None, message = None, *args):
    return json.encode(get_error(code, key = key, message = None, *args))

def get_error(code, key = None, message = None, *args):
    if key: 
        return {'code' : code, 'message' : settings.API_CODES[code][key]}
    elif message:
        return {'code' : code, 'message' : message}
    else:
        return {'code' : code, 'message' : settings.API_CODES[code]}
    
def logapi(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug("API call: %s args: %s kwargs: %s" % (func.__name__, args[1:], kwargs))
        res = func(*args, **kwargs)
        logging.debug("API call: %s result: %s" % (func.__name__, res))
        return res
    
    return wrapper

def loghandler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug("HTML Request: %s args: %s kwargs: %s" % (func.__name__, args[1:], kwargs))
        res = func(*args, **kwargs)
        return res
    
    return wrapper
                
class BaseHandler(webapp2.RequestHandler):
    # if we don't have this then spammy head requests would clutter the error log
    def head(self):
        pass
        
    def handle_exception(self, exception, debug_mode):    
        logging.exception(exception)
        if debug_mode:
            lines = ''.join(traceback.format_exception(*sys.exc_info()))
            self.response.clear()
            self.response.write('<pre>%s</pre>' % (cgi.escape(lines, quote=True)))
        else:
            self.abort(404)
            
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)
        
    @webapp2.cached_property
    def session(self):
        session = self.session_store.get_session()
        
        if len(session) == 0:
            for k, v in settings.COOKIE_TEMPLATE.iteritems(): 
                session[k] = v
        
            # initialize random session ID
            session['id'] = hashlib.md5(os.urandom(16)).hexdigest()
        # Returns a session using the default cookie key.
        return session
    
    @webapp2.cached_property
    def auth(self):
        return auth.get_auth()
  
    @webapp2.cached_property
    def current_user(self):
        """Returns currently logged in user"""
        user_dict = self.auth.get_user_by_session()
        return self.auth.store.user_model.get_by_id(user_dict['user_id'])
      
    @webapp2.cached_property
    def logged_in(self):
        """Returns true if a user is currently logged in, false otherwise"""
        return self.auth.get_user_by_session() is not None
        
    def session_regenerate_id(self):
        self.session['id'] = hashlib.md5(os.urandom(16)).hexdigest()
        
    def session_inc_pageviews(self):
        self.session['pageviews'] = self.session['pageviews'] + 1
    
    def session_login(self):
        self.session['authed'] = True
    
    def session_logout(self):
        self.session['authed'] = False
    
    def prep_html_response(self, template_name, template_vars={}):
        # Preset values for the template
        values = {
          'url_for'      : self.uri_for,
          'logged_in'    : self.logged_in,
          'current_user' : self.current_user if self.logged_in else None
        }
        
        # Add manually supplied template values
        values.update(template_vars)
        
        logging.info("session: %s" % self.session)
        logging.info("template vars: %s" % values)
        
        try:
            template = jinja_environment.get_template(template_name)
            self.response.out.write(template.render(**values))
        except TemplateNotFound:
            self.abort(404)

class BaseAPIHandler(BaseHandler):
    def prep_json_response(self, code, key = None, message = None, *args):
        self.response.set_status(code)
        self.response.write(get_json_error(code, key = key, message = message, *args))
    
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
            result = get_error(500, message = lines) 
        else:
            result = get_error(500, key = 'admin_required') 
            
        self.response.clear()
        self.response.write(json.encode(result))
        
    def get(self, *args):
        action = self.request.get('action')
        args = self.request.GET
        
        args['user'] = model.User.get_user_from_session(self.session['id'])
        for arg in args:
            args[arg] = self.request.get(arg)
        
        if not 'action' in args or not args['action'] in settings.APIS:
            result = get_error(400, key = 'unsupported')
        else:    
            result = getattr(self, action)(args)
        
        self.response.clear()
        self.response.set_status(result['code'])
        self.response.write(json.encode(result))

    def put(self):
        pass
    
    def post(self):
        pass
    
    def delete(self):
        pass
    
class BaseRESTHandler(BaseAPIHandler):
        
    def get(self, obj_t, identifier, *args):
        cls = getattr(sys.modules['model'], obj_t)
        obj = cls.get(identifier)
        return json.encode(obj)
    
    def put(self, obj_t, identifier, *args):
        kvs = json.decode(self.request.body)
        cls = getattr(sys.modules['model'], obj_t, kvs)
        obj = cls.put(identifier)
        return json.encode(obj)
    
    def post(self, obj_t, identifier, *args):
        kvs = json.decode(self.request.body)
        cls = getattr(sys.modules['model'], obj_t, kvs)
        obj = cls.post(identifier)
        return json.encode(obj)
    
    def delete(self, obj_t, identifier, *args):
        cls = getattr(sys.modules['model'], obj_t)
        obj = cls.delete(identifier)
        return json.encode(obj)
    
def handle_404(request, response, exception):
    template = jinja_environment.get_template("404.html")
    response.set_status(404)
    response.out.write(template.render())
    

    