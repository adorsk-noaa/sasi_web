from flask import Flask, request, Response, json

import sasi.sa.session as sa_session
from sasi.dao.habitat.sa_habitat_dao import SA_Habitat_DAO
import sasi.viz.habitat.map.mapserver as habitat_ms

app = Flask(__name__)
app.debug = True


@app.route('/getmap')
def get_map():

	# Get a session.
	session = sa_session.get_session()

	# Create habitat DAO.
	habitat_dao = SA_Habitat_DAO(session=session)

	# Parse parameters into custom and WMS parameters.
	custom_parameters = []
	custom_parameters_json = request.args.get('PARAMS','[]')
	if custom_parameters_json:
		custom_parameters = json.loads(custom_parameters_json)
	wms_parameters = request.args.items()

	# Assemble filters from custom parameters.
	# @TODO
	filters = []
	for p in custom_parameters:
		f = {
				'attr': p[0],
				'op': p[1],
				'value': p[2]
				}
		filters.append(f)

	# Generate map image for the given parameters.
	map_image = habitat_ms.get_map_image_from_wms(wms_parameters=wms_parameters, habitat_dao=habitat_dao, filters=filters) 

	# Return the image.
	return Response(map_image, mimetype='image/gif')

if __name__ == '__main__':
	app.run()

