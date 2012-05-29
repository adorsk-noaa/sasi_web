from flask import Flask, request, Response, json, jsonify, send_file
from flaskext.cache import Cache
import results_services
import sasi.sa.session as sa_session
import os

app = Flask(__name__)

app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = '/var/cache/sasi/results/app'
cache = Cache(app)

from xdomain import *


# Define teardown for closing db connections.
@app.teardown_request
def teardown_request(exception):
	sa_session.close_session()
	

def make_cache_key():
	return "%s" % (request.url)


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

	facet = results_services.get_choice_facet(
			id_field=id_field,
			value_field=value_field,
			label_field=label_field,
			filters=filters,
			aggregate_func=aggregate_func
			)

	return Response(json.dumps(facet, indent=2), mimetype='application/json')

@app.route('/get_numeric_facet/')
@crossdomain(origin='*')
@cache.cached(key_prefix=make_cache_key)
def get_numeric_facet():

	value_field_json = request.args.get('VALUE_FIELD', '')
	value_field = json.loads(value_field_json)

	grouping_field_json = request.args.get('GROUPING_FIELD', '')
	grouping_field = json.loads(grouping_field_json)

	base_filters_json = request.args.get('BASE_FILTERS','[]')
	if base_filters_json: base_filters = json.loads(base_filters_json)
	else: base_filters = []

	filters_json = request.args.get('FILTERS','[]')
	if filters_json: filters = json.loads(filters_json)
	else: filters = []

	facet = results_services.get_numeric_facet(
			value_field=value_field,
			grouping_field=grouping_field,
			base_filters=base_filters,
			filters=filters,
			)

	return Response(json.dumps(facet, indent=2), mimetype='application/json')

@app.route('/get_totals/')
@crossdomain(origin='*')
#@cache.cached(key_prefix=make_cache_key)
def get_totals():

	value_field = request.args.get('VALUE_FIELD', '')

	base_filters_json = request.args.get('BASE_FILTERS','[]')
	if base_filters_json: base_filters = json.loads(base_filters_json)
	else: base_filters = []

	filters_json = request.args.get('FILTERS','[]')
	if filters_json: filters = json.loads(filters_json)
	else: filters = []

	totals = results_services.get_totals(
			value_field=value_field,
			base_filters=base_filters,
			filters=filters,
			)

	return Response(json.dumps(totals, indent=2), mimetype='application/json')

@app.route('/get_aggregates/')
@crossdomain(origin='*')
#@cache.cached(key_prefix=make_cache_key)
def get_aggregates():

	value_fields_json = request.args.get('VALUE_FIELDS', '')
	if value_fields_json: value_fields = json.loads(value_fields_json)
	else: value_fields= []

	grouping_fields_json = request.args.get('GROUPING_FIELDS', '')
	if grouping_fields_json: grouping_fields = json.loads(grouping_fields_json)
	else: grouping_fields = []

	filters_json = request.args.get('FILTERS','[]')
	if filters_json: filters = json.loads(filters_json)
	else: filters = []

	with_unfiltered = request.args.get('WITH_UNFILTERED','FALSE')
	if with_unfiltered == 'TRUE': with_unfiltered = True
	else: with_unfiltered = False

	base_filters_json = request.args.get('BASE_FILTERS','[]')
	if base_filters_json: base_filters = json.loads(base_filters_json)
	else: base_filters = []

	aggregates = results_services.get_aggregates(
			value_fields=value_fields,
			grouping_fields=grouping_fields,
			filters=filters,
			with_unfiltered=with_unfiltered,
			base_filters=base_filters
			)

	return Response(json.dumps(aggregates, indent=2), mimetype='application/json')

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

	result_field_json = request.args.get('RESULT_FIELD','{}')
	result_field = json.loads(result_field_json)

	filters_json = request.args.get('FILTERS','[]')
	if filters_json: filters = json.loads(filters_json)
	else: filters = []

	map_image = results_services.get_map(wms_parameters=wms_parameters, filters=filters, result_field=result_field)

	# Return the image.
	return Response(map_image, mimetype='image/gif')


if __name__ == '__main__':
	session = sa_session.get_session()
	app.run(debug=True)

