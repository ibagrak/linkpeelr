import webapp2

import settings
from handlers import index, api, common, email_auth

routes = [webapp2.Route('/',                  handler = index.Index),
          
          # email authentication routes
          webapp2.Route('/email-confirm',     handler = email_auth.EmailConfirm),
          webapp2.Route('/email-signin',      handler = email_auth.EmailAuthHandler, handler_method="signin_email"),
          webapp2.Route('/email-signup',      handler = email_auth.EmailAuthHandler, handler_method="signup_email"),
          
          # oauth authentication routes
          webapp2.Route('/auth/<provider>',   handler='handlers.oauth.AuthHandler:_simple_auth', name='auth_login'),
          webapp2.Route('/auth/<provider>/callback', handler='handlers.oauth.AuthHandler:_auth_callback', name='auth_callback'),
          
          # common logout
          webapp2.Route('/logout', handler='handlers.oauth.AuthHandler:logout', name='logout'),
          
          # REST API
          webapp2.Route('/rest/<obj_t>/<id>', handler = common.BaseRESTHandler), 
          
          # RPC API
          webapp2.Route('/rpc',               handler = api.RPCHandler), 
          ]                             
                                       
application = webapp2.WSGIApplication(routes,   
                                      debug = settings.DEBUG,
                                      config = settings.app_config)

application.error_handlers[404] = common.handle_404

def main():
    application.run()

if __name__ == "__main__":
    main()