from flask import Flask, request, Response, json, jsonify

import sasi.sa.session as sa_session
from sasi.dao.habitat.sa_habitat_dao import SA_Habitat_DAO

app = Flask(__name__)
app.debug = True


@app.route('/get_facets')
def get_facets():

	# Get a session.
	session = sa_session.get_session()

	# Create habitat DAO.
	habitat_dao = SA_Habitat_DAO(session=session)

	# Assemble facets.
	facets = []

	# Substrates.
	substrate_facets = get_substrate_facets(habitat_dao=habitat_dao)
	facets.extend(substrate_facets)

	# Energy levels.
	energy_facets = get_energy_facets(habitat_dao=habitat_dao)
	facets.extend(energy_facets)

	# Features.
	feature_facets = []
	facets.extend(feature_facets)

	# Return facets.
	return jsonify(facets=facets)


def get_substrate_facets(habitat_dao=None, filters=None): 

	# Get available substrates for habitats.
	substrates = habitat_dao.get_substrates_for_habitats(filters=filters)

	# Assemble options for facet.
	options = [[s.name, s.id] for s in substrates]
	options.sort(key=lambda o:o[0])

	# Assemble facet.
	facet = {
			'label': 'Substrates',
			'id': 'Habitat_Type.Substrate.id',
			'type': 'multiselect',
			'options': options
			}

	return [facet]


def get_energy_facets(habitat_dao=None, filters=None): 

	# Get available energy levels for habitats.
	energys = habitat_dao.get_energys_for_habitats(filters=filters)

	# Assemble options for facet.
	options = [[energy, energy] for energy in energys]
	options.sort(key=lambda o:o[0])

	# Assemble facet.
	facet = {
			'label': 'Energy',
			'id': 'Habitat_Type.energy',
			'type': 'multiselect',
			'options': options
			}

	return [facet]


# HERE!!!
# TODO
def get_feature_facets(habitat_dao=None, filters=None): pass

if __name__ == '__main__':
	app.run()

