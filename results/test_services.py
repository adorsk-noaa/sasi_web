import results_services

def main():
	base_filters = [
			{'field': 'time', 'op': '==', 'value': '2008'},
			{'field': 'tag', 'op': '==', 'value': 'gc30_all'}
			]

	# Test get image.
	wms_parameters = {
			'SERVICE': 'WMS' ,
			'VERSION': '1.1.0', 
			'REQUEST': 'GetMap', 
			'LAYERS': 'data',
			'SRS':'EPSG:4326',
			#'BBOX':'-180.0,-90.0,180.0,90.0',
			'BBOX': '-80,31,-65,45',
			'FORMAT':'image/gif',
			'WIDTH':'640',
			'HEIGHT':'640',
			}
		
	result_field = {
			'field': 'A'
			}
	map_img = results_services.get_map(wms_parameters=wms_parameters.items(), filters=base_filters, result_field=result_field)
	#print map_img
	


if __name__ == '__main__': main()
