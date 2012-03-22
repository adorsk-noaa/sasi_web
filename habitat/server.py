from cherrypy import wsgiserver
from habitat_app import app
import tilecache
from StringIO import StringIO

port = 8080

tilecache_config = """
[cache]
type=Disk
base=/tmp/tilecache

[habitat]
type=WMS
url=http://localhost:%s/habitat/app/get_map?TRANSPARENT=TRUE
bbox=-78.4985,32.1519,-65.7055,44.7674
maxResolution=0.025
levels=5
extension=png
""" % port

tilecache.config_file_handle = StringIO(tilecache_config)

d = wsgiserver.WSGIPathInfoDispatcher({
'/habitat/app': app,
'/habitat/cache': tilecache.app
})

server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', port),d)

if __name__ == '__main__':
	try: server.start()
	except KeyboardInterrupt: server.stop()
