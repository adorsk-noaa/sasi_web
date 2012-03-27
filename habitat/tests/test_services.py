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
			value_field=value_field, 
			filters=filters, 
			)

	#print numeric_facet['unfiltered_histogram']
	#print numeric_facet['filtered_histogram']

if __name__ == '__main__': main()
