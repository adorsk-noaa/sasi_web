from flask import Flask, request, Response, json, jsonify
import baselayers_services

app = Flask(__name__)
app.debug = True

from xdomain import *

@app.route('/get_map')
@crossdomain(origin='*')
def get_map():

	wms_parameters = request.args.items()

	map_image = baselayers_services.get_map(wms_parameters=wms_parameters)

	# Return the image.
	return Response(map_image, mimetype='image/gif')


if __name__ == '__main__':
	app.run(port=5001)

