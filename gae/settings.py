import os
from google.appengine.api.app_identity import get_default_version_hostname, get_application_id

from secrets import SESSION_KEY

if 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    DEBUG = True
    HOME_URL = 'http://localhost' + ':8086'
else:
    DEBUG = False
    HOME_URL = 'http://' + get_default_version_hostname()

# webapp2 config
app_config = {
  'webapp2_extras.sessions': {
    'cookie_name': '_simpleauth_sess',
    'secret_key': SESSION_KEY
  },
  'webapp2_extras.auth': {
    'user_attributes': []
  }
}

# i18n config
AVAILABLE_LOCALES = ['en_US']

# List of valid APIs
APIS = frozenset(['peel', 'peel_all', 'last'])

#200 OK - Everything worked as expected.
#400 Bad Request - Often missing a required parameter.
#401 Unauthorized - No valid API key provided.
#402 Request Failed - Parameters were valid but request failed.
#404 Not Found - The requested item doesn't exist.
#500, 502, 503, 504 Server errors - something went wrong on Stripe's end.

API_CODES  = { 200 : 'Success', 
               301 : 'Moved permanently', 
               302 : 'Found',
               400 : {'unsupported'    : 'API not supported'}, 
               401 : {}, 
               402 : {'failed'         : 'Download failed'},
               404 : {'dne'            : 'Does not exist'},
               405 : {'not_allowed'    : 'Method not allowed'}, 
               500 : {'generic'        : 'Server error'}}

LEGACY_API_CODES = {
  'OK' : 0,
  'INVALID_API_ERROR' : 1,
  'INVALID_URL_ERROR' : 2,
  'DOWNLOAD_ERROR' : 3,
  'GENERAL_ERROR' : 4, 
  200 : 200,
  301 : 301, 
  302 : 302,
  400 : 1,
  404 : 2, 
  402 : 3, 
  405 : 4, 
  500 : 4,
}

# URLs
APP_ID = get_application_id()

COOKIE_TEMPLATE = { 'id'        : 0,     #session id
                    'pageviews' : 0, 
                    'authed'    : False, 
                    'active'    : True }

DATE_FORMAT_HTML = "dd-mm-yyyy"
DATE_FORMAT = "%d-%m-%Y"

# Email Authentication
EMAIL_CONFIRM_BODY = """ 
Hello, %s!

Please click the link below to confirm your email address: 

%s

Thank you. 
""" 

EMAIL_SENDER = "ilya.bagrak@gmail.com"
