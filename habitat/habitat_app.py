from flask import Flask, request, Response, json, jsonify
import habitat_services

app = Flask(__name__)
app.debug = True

from xdomain import *

@app.route('/get_facet/')
@crossdomain(origin='*')
def get_facet():

	id_field = request.args.get('ID_FIELD', '')
	label_field = request.args.get('LABEL_FIELD', '')
	value_field = request.args.get('VALUE_FIELD', '')
	aggregate_func = request.args.get('AGGREGATE_FUNC', 'sum')

	filters_json = request.args.get('FILTERS','[]')
	if filters_json: filters = json.loads(filters_json)
	else: filters = []

	facet = habitat_services.get_facet(
			id_field=id_field,
			value_field=value_field,
			label_field=label_field,
			filters=filters,
			aggregate_func=aggregate_func
			)

	return Response(json.dumps(facet, indent=2), mimetype='application/json')

@app.route('/get_map')
@crossdomain(origin='*')
def get_map():

	# Parse parameters into custom and WMS parameters.
	custom_parameters = []
	custom_parameters_json = request.args.get('PARAMS','[]')
	if custom_parameters_json:
		custom_parameters = json.loads(custom_parameters_json)
	wms_parameters = request.args.items()

	# Assemble filters from custom parameters.
	# @TODO
	filters = []
	print "parms is: %s" % custom_parameters
	for p in custom_parameters:

		# Handle feature parameters specially, to account for categories.
		if 'Feature-' in p[0]:
			p[0] = re.sub('Feature-(Biological|Geological)', 'Feature', p[0])

		f = {
				'attr': p[0],
				'op': p[1],
				'value': p[2]
				}
		filters.append(f)

	map_image = habitat_services.get_map(wms_parameters=wms_parameters, filters=filters)

	# Return the image.
	return Response(map_image, mimetype='image/gif')


if __name__ == '__main__':
	app.run()

