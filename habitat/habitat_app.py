from flask import Flask, request, Response, json, jsonify, send_file
from flaskext.cache import Cache
import habitat_services
import sasi.sa.session as sa_session

app = Flask(__name__)
app.debug = True

app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = '/tmp/mycache'
cache = Cache(app)

from xdomain import *

def make_cache_key():
	return "%s" % (request.url)

@app.route('/get_export/')
@crossdomain(origin='*')
@cache.cached(key_prefix=make_cache_key)
def get_export():
	export_type = request.args.get('TYPE','csv')
	filters_json = request.args.get('FILTERS','[]')
	if filters_json: filters = json.loads(filters_json)
	else: filters = []

	if export_type == 'csv':
		resp = Response(
				habitat_services.get_export(type='csv', filters=filters),
				mimetype='text/csv'
				)
		resp.headers['Content-Disposition'] = 'attachment; filename=habitats.csv'
		return resp


@app.route('/get_choice_facet/')
@crossdomain(origin='*')
@cache.cached(key_prefix=make_cache_key)
def get_choice_facet():

	id_field = request.args.get('ID_FIELD', '')
	label_field = request.args.get('LABEL_FIELD', '')
	value_field = request.args.get('VALUE_FIELD', '')
	aggregate_func = request.args.get('AGGREGATE_FUNC', 'sum')

	filters_json = request.args.get('FILTERS','[]')
	if filters_json: filters = json.loads(filters_json)
	else: filters = []

	facet = habitat_services.get_choice_facet(
			id_field=id_field,
			value_field=value_field,
			label_field=label_field,
			filters=filters,
			aggregate_func=aggregate_func
			)

	return Response(json.dumps(facet, indent=2), mimetype='application/json')

@app.route('/get_numeric_facet/')
@crossdomain(origin='*')
#@cache.cached(key_prefix=make_cache_key)
def get_numeric_facet():

	value_field = request.args.get('VALUE_FIELD', '')

	base_filters_json = request.args.get('BASE_FILTERS','[]')
	if base_filters_json: base_filters = json.loads(base_filters_json)
	else: base_filters = []

	filters_json = request.args.get('FILTERS','[]')
	if filters_json: filters = json.loads(filters_json)
	else: filters = []

	facet = habitat_services.get_numeric_facet(
			value_field=value_field,
			base_filters=base_filters,
			filters=filters,
			)

	return Response(json.dumps(facet, indent=2), mimetype='application/json')


@app.route('/get_map')
@crossdomain(origin='*')
@cache.cached(key_prefix=make_cache_key)
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
	print "request url is: %s" % request.url
	print "parms is: %s" % custom_parameters
	for p in custom_parameters:

		# Handle feature parameters specially, to account for categories.
		if 'Feature-' in p['field']:
			p['field'] = re.sub('Feature-(Biological|Geological)', 'Feature', p['field'])

		filters.append(p)

	map_image = habitat_services.get_map(wms_parameters=wms_parameters, filters=filters)

	# Return the image.
	return Response(map_image, mimetype='image/gif')


if __name__ == '__main__':
	session = sa_session.get_session()
	app.run()

