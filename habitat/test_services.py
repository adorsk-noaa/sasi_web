import habitat_services

def main():
	facet_id = 'habitat_type.substrate.id'
	facet_label = 'Substrates'
	facet_type = 'multiselect'
	id_field = 'habitat_type.substrate.id'
	label_field = 'habitat_type.substrate.name'
	value_field = 'area'
	filters = []
	aggregate_func = 'sum'

	choice_facet = habitat_services.get_choice_facet(
			id_field=id_field, 
			value_field=value_field, 
			label_field=label_field, 
			filters=filters, 
			aggregate_func=aggregate_func
			)
	#print choice_facet

	numeric_facet = habitat_services.get_numeric_facet(
			grouping_field={ 'id':'z', 'transform': '-1 * {field}' },
			value_field={'id': 'area'},
			filters=[
				{'field': 'habitat_type.substrate.id', 'op': 'in', 'value': ['S1']}
				]
			)

	totals = habitat_services.get_totals(value_field='area', filters=[])
	#print totals

	# Test aggregates.
	value_fields = [
			{
				'id': 'area',
				'aggregate_funcs': ['sum']
				}
			]

	grouping_fields = [
			#{'id': "habitat_type.substrate.id", 'label': 'substrate_id', 'label_field': {'id': 'habitat_type.substrate.name'}, 'all_values': True},
			{ 'id':'z', 'transform': '-1 * {field}', 'as_histogram': True, 'all_values': True},
			]
	filters = []
	aggregates = habitat_services.get_aggregates(
			value_fields = value_fields,
			grouping_fields = grouping_fields,
			filters = filters
			)
	#print aggregates

	# Test aggregates w/ unfiltered.
	uf_aggregates = habitat_services.get_aggregates(
			value_fields = value_fields,
			grouping_fields = grouping_fields,
			filters = [ 
				{'field': 'habitat_type.substrate.id', 'op': 'in', 'value': ['S1']}
				],
			with_unfiltered = True
			)

	#print uf_aggregates

	#csv_export = habitat_services.get_export(type='csv', filters=[])
	#print csv_export

if __name__ == '__main__': main()
