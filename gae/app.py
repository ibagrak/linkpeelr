import webapp2

import settings
from handlers import index, api, common, locale

routes = [webapp2.Route('/',                handler = index.Index),
          
          # i18n manual locale change
          webapp2.Route('/locale/<locale>', handler = locale.SetLocale),
          
          # RPC API
          webapp2.Route('/rpc/<action>',    handler = api.RPCHandler), 
          
          webapp2.Route('/api',             handler = api.LegacyRPCHandler),

          ]                             
                                       
application = webapp2.WSGIApplication(routes,   
                                      debug = settings.DEBUG,
                                      config = settings.app_config)

application.error_handlers[404] = common.handle_404

def main():
    application.run()
