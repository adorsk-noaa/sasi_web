import sasi.sa.session as sa_session
from sasi.dao.habitat.sa_habitat_dao import SA_Habitat_DAO
import sasi.viz.habitat.map.mapserver as habitat_ms
from sasi.exporters.habitat import csv_exporter
from sasi.exporters.habitat import shp_exporter

import re
import os
import copy

def get_dao():
	session = sa_session.get_session()
	return SA_Habitat_DAO(session=session)

def get_export(type=None, filters=None):
	habitat_dao = get_dao()

	habitats = habitat_dao.get_habitats(filters=filters)

	if type == 'csv':
		exporter = csv_exporter.CsvExporter()
		return exporter.export(habitats)

	if type == 'shp':
		exporter = shp_exporter.ShpExporter()
		return exporter.export(habitats)


def get_choice_facet(id_field=None, value_field=None, label_field=None, filters=None, aggregate_func='sum'):
	habitat_dao = get_dao()

	# We use the current PID to create unique labels.
	pid = "%s" % os.getpid()
	id_label = '%s_id' % pid
	label_label = '%s_label' % pid
	value_label = '%s_value' % pid

	# Get aggregates for choices.
	aggregates = habitat_dao.get_aggregates(
			fields=[{
				'id': value_field, 
				'label': value_label,
				'aggregate_funcs': [aggregate_func],
				}],
			grouping_fields=[{
				'id': id_field,
				'label': id_label,
				label_field: {'id': label_field, 'label': label_label}
				}],
			filters=filters 
			)

	# Assemble facet choices from aggregates.
	choices = []
	for leaf in aggregates.get('children', {}).values():
		choices.append({
			"id": leaf['id'],
			"label": leaf['label'],
			"count": leaf['data'][0]['value']
			})

	choices.sort(key=lambda o:o['label'])

	# Get total for value field.
	total = aggregates['data'][0]['value']

	# Assemble facet.
	facet = {
			'choices': choices,
			'value_total': total
			}

	return facet


def get_numeric_facet(value_field=None, grouping_field=None, base_filters=[], filters=[]):

	# Set properties on grouping field.
	grouping_field['as_histogram'] = True
	grouping_field['all_values'] = True
	grouping_field.setdefault('num_buckets', 25)

	# Get filtered and unfiltered aggregates.
	aggregates = get_aggregates(
			value_fields = [value_field],
			grouping_fields = [grouping_field],
			filters=filters,
			with_unfiltered=True,
			base_filters=base_filters
			)

	# Assemble histograms
	base_histogram = []
	filtered_histogram = []

	for node in aggregates.get('children', {}).values():

		# Get min/max from label.
		bucket_label = node['label']
		bucket_min = ""
		bucket_max = ""
		m = re.match('(.*) to (.*)', bucket_label)
		if m:
			bucket_min = float(m.group(1))
			bucket_max = float(m.group(2))

		base_bucket = {
				'bucket': node['label'],
				'min': bucket_min,
				'max': bucket_max,
				'count': node['data'][0]['value']
				}
		base_histogram.append(base_bucket)

		filtered_bucket = base_bucket.copy()
		filtered_bucket['count'] = node['data'][1]['value']
		filtered_histogram.append(filtered_bucket)

	for h in [base_histogram, filtered_histogram]:
		h.sort(key=lambda b: b['min'])
        
	# Assemble facet
	facet = {
			'base_histogram': base_histogram,
			'filtered_histogram': filtered_histogram,
			}

	return facet


def get_map(wms_parameters=None, filters=None):
	habitat_dao = get_dao()

	# Generate map image for the given parameters.
	map_image = habitat_ms.get_map_image_from_wms(wms_parameters=wms_parameters, habitat_dao=habitat_dao, filters=filters) 

	# Return the image.
	return map_image

def get_totals(value_field=None, base_filters=[], filters=[]):
	habitat_dao = get_dao()
	value_field = {'id': value_field, 'label': 'value_field', 'aggregate_funcs': ['sum']}

	# Get filtered and unfiltered aggregates.
	aggregates = get_aggregates(
			value_fields = [value_field],
			filters=filters,
			with_unfiltered=True,
			base_filters=base_filters
			)

	# Assemble totals
	totals = {
			'filtered_total': aggregates['data'][0]['value'],
			'unfiltered_total': aggregates['data'][1]['value'],
			}

	return totals


def get_aggregates(value_fields=None, grouping_fields=[], filters=[], with_unfiltered=False, base_filters=[]):
	habitat_dao = get_dao()

	for vf in value_fields: 
		vf.setdefault('label', "{}--label".format(vf.get('id')))

	aggregates = habitat_dao.get_aggregates(
			fields=value_fields,
			grouping_fields=grouping_fields,
			filters=filters)

	if with_unfiltered:
		unfiltered_value_fields = copy.deepcopy(value_fields)
		for vf in unfiltered_value_fields:
			vf['label'] += '--unfiltered'

		unfiltered_aggregates = habitat_dao.get_aggregates(
				fields=unfiltered_value_fields,
				grouping_fields=grouping_fields,
				filters=base_filters
				)

		# Make path dicts for each tree.
		filtered_path_dict = {}
		unfiltered_path_dict = {}
		update_path_dict(aggregates, tuple(), filtered_path_dict)
		update_path_dict(unfiltered_aggregates, tuple(), unfiltered_path_dict)

		# Add unfiltered data to filtered data.
		for path, filtered_node in filtered_path_dict.items():
			unfiltered_node = unfiltered_path_dict.get(path)
			for d in unfiltered_node['data']:
				filtered_node['data'].append(d)
	

	return aggregates

# Helper function to make a dictionary of path:leaf pairs for a given tree node.
def update_path_dict(node, path, path_dict):
	cur_path = path + (node.get('id'),)

	path_dict[cur_path] = node

	if node.has_key('children'):
		for c in node['children'].values():
			update_path_dict(c, cur_path, path_dict)



	
