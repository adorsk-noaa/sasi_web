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
url=http://localhost:%s/map/get_map
extension=png
""" % port

tilecache.config_file_handle = StringIO(tilecache_config)

d = wsgiserver.WSGIPathInfoDispatcher({
'/map': app,
'/cache': tilecache.app
})

server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', port),d)

if __name__ == '__main__':
	try: server.start()
	except KeyboardInterrupt: server.stop()
