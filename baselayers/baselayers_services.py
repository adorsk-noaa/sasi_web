import sasi.viz.baselayers.map.mapserver as baselayers_ms

def get_map(wms_parameters=None):

	# Generate map image for the given parameters.
	map_image = baselayers_ms.get_map_image_from_wms(wms_parameters=wms_parameters)

	# Return the image.
	return map_image


