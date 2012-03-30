from flask import Flask, request, Response, json, jsonify
from flaskext.cache import Cache
import baselayers_services

app = Flask(__name__)
app.debug = True

app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = '/var/cache/sasi/basemap/app'
cache = Cache(app)

from xdomain import *

def make_cache_key():
	return "%s" % (request.url)

@app.route('/get_map')
@crossdomain(origin='*')
@cache.cached(key_prefix=make_cache_key)
def get_map():
	wms_parameters = request.args.items()

	map_image = baselayers_services.get_map(wms_parameters=wms_parameters)

	# Return the image.
	return Response(map_image, mimetype='image/gif')


if __name__ == '__main__':
	app.run(port=5001)

