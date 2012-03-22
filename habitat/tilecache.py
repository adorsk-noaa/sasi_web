import os, sys
from TileCache.Service import Service, wsgiHandler

tilecachepath, wsgi_file = os.path.split(__file__)
 
config_file_handle = None

theService = {}
def wsgiApp (environ, start_response):
    global theService, config_file
    if not theService:
        theService = Service.load((config_file_handle))
    return wsgiHandler(environ, start_response, theService)
 
app = wsgiApp
