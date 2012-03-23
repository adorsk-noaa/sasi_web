import sasi.sa.session as sa_session
from sasi.dao.habitat.sa_habitat_dao import SA_Habitat_DAO
import sasi.viz.habitat.map.mapserver as habitat_ms
import re
import os

def get_facet(id_field=None, value_field=None, label_field=None, filters=None, aggregate_func='sum'):

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


def get_map(wms_parameters=None, filters=None):

	# Get a session.
	session = sa_session.get_session()

	# Create habitat DAO.
	habitat_dao = SA_Habitat_DAO(session=session)

	# Generate map image for the given parameters.
	map_image = habitat_ms.get_map_image_from_wms(wms_parameters=wms_parameters, habitat_dao=habitat_dao, filters=filters) 

	# Return the image.
	return map_image


