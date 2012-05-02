import sasi.sa.session as sa_session
from sasi.dao.habitat.sa_habitat_dao import SA_Habitat_DAO
import sasi.viz.habitat.map.mapserver as habitat_ms
from sasi.exporters.habitat import csv_exporter
from sasi.exporters.habitat import shp_exporter

import re
import os

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


def get_numeric_facet(value_field=None, base_filters=[], filters=[]):
	habitat_dao = get_dao()

	bucket_field = {'id': value_field, 'label': 'bucket_field'}

	# Get base field min and max.
	# We use the same min and max for base and filtered
	# to provide a common reference scale.
	aggregate_field = bucket_field.copy()
	aggregate_field['aggregate_funcs'] = ['min', 'max']
	aggregates = habitat_dao.get_aggregates(
			fields=[aggregate_field],
			filters=base_filters)
	field_min = float(aggregates['data'][0]['value'])
	field_max = float(aggregates['data'][1]['value'])

	# Get unfiltered histogram.
	base_histogram = habitat_dao.get_histogram(
			bucket_field=bucket_field,
			field_max=field_max,
			field_min=field_min,
			num_buckets=25,
			filters=base_filters,
			)

	# Get filtered histogram.
	filtered_histogram = habitat_dao.get_histogram(
			bucket_field=bucket_field,
			field_max=field_max,
			field_min=field_min,
			num_buckets=25,
			filters=filters
			)

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

	unfiltered_aggregates = habitat_dao.get_aggregates(
			fields=[value_field],
			filters=base_filters)
	unfiltered_total = float(unfiltered_aggregates['data'][0]['value'])

	filtered_aggregates = habitat_dao.get_aggregates(
			fields=[value_field],
			filters=filters)
	filtered_total= float(filtered_aggregates['data'][0]['value'])

	# Assemble totals
	totals = {
			'unfiltered_total': unfiltered_total,
			'filtered_total': filtered_total,
			}

	return totals


def get_aggregates(value_fields=None, grouping_fields=[], filters=[]):
	habitat_dao = get_dao()

	aggregates = habitat_dao.get_aggregates(
			fields=value_fields,
			grouping_fields=grouping_fields,
			filters=filters)

	return aggregates
