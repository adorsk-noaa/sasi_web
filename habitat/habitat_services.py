import sasi.sa.session as sa_session
from sasi.dao.habitat.sa_habitat_dao import SA_Habitat_DAO
import sasi.viz.habitat.map.mapserver as habitat_ms
from sasi.exporters.habitat import csv_exporter

import re
import os

def get_export(type=None, filters=None):
	session = sa_session.get_session()
	habitat_dao = SA_Habitat_DAO(session=session)
	habitats = habitat_dao.get_habitats(filters=filters)

	if type == 'csv':
		exporter = csv_exporter.CsvExporter()
		return exporter.export(habitats)


def get_choice_facet(id_field=None, value_field=None, label_field=None, filters=None, aggregate_func='sum'):

	# Get a session.
	session = sa_session.get_session()

	# Create habitat DAO.
	habitat_dao = SA_Habitat_DAO(session=session)

	# We use the current PID to create unique labels.
	pid = "%s" % os.getpid()
	id_label = '%s_id' % pid
	label_label = '%s_label' % pid
	value_label = '%s_value' % pid

	# Get aggregates for choices.
	aggregates = habitat_dao.get_aggregates(
			fields=[{'id': value_field, 'label': value_label}],
			grouping_fields=[
				{'id': id_field, 'label': id_label},
				{'id': label_field, 'label': label_label}
				],
			filters=filters, 
			aggregate_funcs = [aggregate_func],
			as_dicts=True
			)

	# Assemble facet choices from aggregates.
	choices = []
	for a in aggregates:
		choices.append({
			"id": a[id_label],
			"label": a[label_label],
			"count": a["%s--%s" % (value_label, aggregate_func)]
			})

	choices.sort(key=lambda o:o['label'])

	# Get total for value field.
	value_total_aggregates = habitat_dao.get_aggregates(
			fields=[{'id': value_field, 'label': value_label}],
			filters=filters, 
			aggregate_funcs = [aggregate_func],
			as_dicts=True
			)
	value_total = value_total_aggregates[0]['%s--%s' % (value_label, aggregate_func)]

	# Assemble facet.
	facet = {
			'choices': choices,
			'value_total': value_total
			}

	return facet


def get_numeric_facet(value_field=None, base_filters=[], filters=[]):

	# Get a session.
	session = sa_session.get_session()

	# Create habitat DAO.
	habitat_dao = SA_Habitat_DAO(session=session)

	bucket_field = {'id': value_field, 'label': 'bucket_field'}

	# Get base field min and max.
	# We use the same min and max for base and filtered
	# to provide a common reference scale.
	aggregates = habitat_dao.get_aggregates(
			fields=[bucket_field],
			aggregate_funcs=['min','max'], 
			filters=base_filters).pop()
	field_max = float(aggregates["%s--max" % bucket_field['label']])
	field_min = float(aggregates["%s--min" % bucket_field['label']])

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

	# Get a session.
	session = sa_session.get_session()

	# Create habitat DAO.
	habitat_dao = SA_Habitat_DAO(session=session)

	# Generate map image for the given parameters.
	map_image = habitat_ms.get_map_image_from_wms(wms_parameters=wms_parameters, habitat_dao=habitat_dao, filters=filters) 

	# Return the image.
	return map_image


