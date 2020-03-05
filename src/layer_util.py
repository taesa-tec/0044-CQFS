# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-09-10
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Geoambiente
        email                : gisti@geoambiente.com.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import logging
import os

from qgis.core import QgsMapLayer, QGis, QgsRasterBandStats, QgsGeometry, QgsRasterLayer, QgsVectorLayer, QgsMapLayerRegistry, QgsCoordinateReferenceSystem, QgsVectorFileWriter, QgsFeature
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from osgeo import gdal
from processing.tools.general import runalg
from constants import CQFS_STYLE
from cqfs_config import load_config, tmp_filename_without_extension

__config = load_config()
__logger = logging.getLogger('layer_util')


def define_crs_if_not_exist():
    __logger.debug('Check if CQFS CRS is defined...')

    config = __config['global']
    name = config['crs_name']
    proj4 = config['crs_proj4']

    crs = QgsCoordinateReferenceSystem()
    crs.createFromProj4(proj4)
    description = str(crs.description())

    if description == '':
        success = crs.saveAsUserCRS(name)
        if success:
            __logger.debug('CRS defined successfully.')
        else:
            __logger.warning('Fail to save CRS "{}".'.format(name))
    else:
        __logger.debug('CRS "{}" already exists.'.format(description))


def layers_name_by_type(layers, layer_type, __sof_=None):
    """
        Get layers name by type.
        If is a vector layer, than the geometry type is valid if is QGis.WKBLineString or QGis.WKBMultiLineString.

        :param layers: self.iface.legendInterface().layers()
        :param layer_type: QgsMapLayer.VectorLayer or QgsMapLayer.RasterLayer
        :param __sof_: Second order function with type validation
        :return: list of valid layers
        """
    layer_list = []
    for layer in layers:
        if layer.type() == layer_type:
            is_valid = True
            if is_vector_layer(layer) and __sof_ and not __sof_(layer):
                is_valid = False
            if is_valid:
                layer_list.append(layer.name())

    layer_list.sort()
    return layer_list


def layers_by_type(layers, layer_type, by_name=None):
    """
    Get layers by type.
    If is a vector layer, than the geometry type is valid if is QGis.WKBLineString or QGis.WKBMultiLineString.

    :param layers: self.iface.legendInterface().layers()
    :param layer_type: QgsMapLayer.VectorLayer or QgsMapLayer.RasterLayer
    :param by_name: list of layers name
    :return: list of valid layers
    """
    layer_list = []
    for layer in layers:
        if layer.type() == layer_type:
            is_valid = True
            if is_vector_layer(layer) and not is_layer_line_or_multiline(layer):
                is_valid = False
            if by_name and not layer.name() in by_name:
                is_valid = False
            if is_valid:
                layer_list.append(layer)
    return layer_list


def find_one_layer_by_name(layers, name):
    for layer in layers:
        if layer.name() == name:
            return layer
    return None


def is_layer_line_or_multiline(layer):
    """
    Check if QgsMapLayer.VectorLayer is QGis.WKBLineString or QGis.WKBMultiLineString.

    :param layer:
    :return: boolean
    """
    return layer.wkbType() in (QGis.WKBLineString, QGis.WKBMultiLineString)


def is_layer_point_or_multipoint(layer):
    """
    Check if QgsMapLayer.VectorLayer is QGis.WKBLineString or QGis.WKBMultiLineString.

    :param layer:
    :return: boolean
    """
    return layer.wkbType() in (QGis.WKBMultiPoint, QGis.WKBPoint)


def is_layer_polygon(layer):
    """
    Check if QgsMapLayer.VectorLayer is QGis.WKBPolygon

    :param layer:
    :return: boolean
    """
    return layer.wkbType() == QGis.WKBPolygon


def is_vector_layer(layer):
    """
    Check if a layer is QgsMapLayer.VectorLayer.

    :param layer: QgsMapLayer.VectorLayer
    :return: boolean
    """
    return layer and layer.type() == QgsMapLayer.VectorLayer


def is_raster_layer(layer):
    """
    Check if a layer is QgsMapLayer.RasterLayer.

    :param layer: QgsMapLayer.RasterLayer
    :return: boolean
    """
    return layer and layer.type() == QgsMapLayer.RasterLayer


def has_correct_crs(layer, proj4):
    """
    Check if QgsMapLayer has the authority identifier for the CRS.

    :param layer: QgsMapLayer
    :param proj4: authority identifier. Example: EPSG:4674.
    :return: boolean
    """
    crs = layer.crs()
    if crs and crs.isValid() and str(crs.toProj4()) == str(proj4):
        return True

    __logger.warn(u'Layer "{}" does not have CRS "{}"'.format(layer.name(), str(proj4)))
    return False


def has_raster_correct_resolution(config, layer):
    """
    :param config: Arguments to be used to validate layer.
    :param layer: QgsRasterLayer
    :return: boolean
    """
    units_per_pixel = int(config['units_per_pixel'])

    digits = 5
    x = int(round(layer.rasterUnitsPerPixelX(), digits))
    y = int(round(layer.rasterUnitsPerPixelX(), digits))

    is_resolution_valid = units_per_pixel == x == y
    if not is_resolution_valid:
        __logger.warn(u'Raster "{}" does not have a valid resolution of {}, got {}.'.format(layer.name(), str(units_per_pixel), str(x)))
        return False

    return True


def has_raster_correct_nodata(config, layer):
    """
    https://gis.stackexchange.com/questions/209855/get-nodata-value-of-raster-in-pyqgis
    https://qgis.org/api/classQgsRasterBlock.html

    :param config: Arguments to be used to validate layer.
    :param layer: QgsRasterLayer
    :return: boolean
    """
    nodata = int(config['nodata'])

    extent = layer.extent()
    provider = layer.dataProvider()
    rows = layer.rasterUnitsPerPixelY()
    cols = layer.rasterUnitsPerPixelX()
    block = provider.block(1, extent, rows, cols)

    has_nodata = block.hasNoData()
    nodata_value = block.noDataValue()
    is_nodata_valid = has_nodata #and nodata_value.is_integer() and int(nodata_value) == nodata
    if not is_nodata_valid:
        str_nodata = str(int(nodata_value)) if has_nodata and nodata_value.is_integer() else 'NaN'
        __logger.warn(u'Raster "{}" does not have a valid nodata {}, got {}.'.format(layer.name(), str(nodata), str_nodata))
        return False

    return True


def has_raster_correct_stats(config, layer):
    """
    :param config: A dict with arguments to be used in validation.
    :param layer: QgsRasterLayer
    :return: boolean
    """
    band_count = int(config['band_count'])
    minimum_value = int(config['minimum_value'])
    maximum_value = int(config['maximum_value'])

    layer_band_count = layer.bandCount()
    if layer_band_count != band_count:
        __logger.warn(u'Raster "{}" does not have a valid band count {}.'.format(layer.name(), str(band_count)))
        return False

    extent = layer.extent()
    provider = layer.dataProvider()
    for band in range(1, layer_band_count + 1):
        stats = provider.bandStatistics(band, QgsRasterBandStats.All, extent, 0)
        min_v = stats.minimumValue
        max_v = stats.maximumValue

        has_valid_range = minimum_value <= min_v and max_v <= maximum_value
        if not has_valid_range:
            __logger.warn(
                u'Raster "{}" band {} does not have a valid min {} and max {}, got {} and {}.'.format(
                    layer.name(),
                    str(band_count),
                    str(minimum_value),
                    str(maximum_value),
                    str(min_v),
                    str(max_v)
                )
            )
            return False
    return True


def buffer_within_rasters(buffer_layer, rasters):
    """
    Check if a geometry with a raster extent.
    https://gis.stackexchange.com/questions/152313/select-polygon-features-that-intersect-a-line-feature-using-pyqgis

    :param buffer_layer:
    :param rasters: list of QgsMapLayer.RasterLayer
    :return: boolean and list of errors
    """
    __logger.info(u'Validating buffer of {} rasters...'.format(str(len(rasters))))

    if not (is_vector_layer(buffer_layer) and int(buffer_layer.featureCount()) == 1 and geom_from_buffer_layer(buffer_layer).type() == QGis.Polygon):
        __logger.warn(u'Layer "{}" is not a VectorLayer'.format(buffer_layer.name()))
        return False

    errors = []
    success = True
    for raster_layer in rasters:
        if not is_raster_layer(raster_layer):
            __logger.warn('Layer "{}" is not a RasterLayer')
            return False

        extent = raster_layer.extent()
        raster_bbox = QgsGeometry.fromWkt(extent.asWktPolygon())

        try:
            within = geom_from_buffer_layer(buffer_layer).within(raster_bbox)
        except Exception as e:
            __logger.warn('Fail to compare buffer_geom.within(raster_bbox): {}'.format(e.message))
            within = None

        if not within:
            if success:
                success = False
            errors.append('Raster "{}" nao preenche toda area do buffer.'.format(raster_layer.name()))

    __logger.info('Rasters validated successfully!')
    return success, errors


def geom_from_buffer_layer(buffer_layer):
    """
    Extract a bbox from a QgsVectorLayer with one row.

    :param buffer_layer: QgsVectorLayer
    :return: QGis.Polygon
    """
    return buffer_layer.getFeatures().next().geometry()


def is_raster_valid(config, layer, proj4):
    """
    :param config: A dict with validations.
    :param layer: QgsRasterLayer
    :param proj4: A string with proj4.
    :return: boolean
    """
    if not is_raster_layer(layer):
        __logger.warn(u'Layer "{}" is not a RasterLayer, got type {}'.format(layer.name(), layer.type()))
        return False

    return has_correct_crs(layer, proj4) and has_raster_correct_resolution(config, layer) and has_raster_correct_nodata(config, layer) and has_raster_correct_stats(config, layer)


def import_layer_qgis(source, suffix=None, base_layer=None, is_vector=False, add_map_layer=True):
    input_layer = base_layer if base_layer else source
    basename = os.path.splitext(os.path.basename(input_layer))[0]
    layer_name = (basename + '_' + suffix) if suffix else basename

    if is_vector:
        layer = QgsVectorLayer(source, layer_name, 'ogr')
    else:
        layer = QgsRasterLayer(source, layer_name)

    if layer.isValid():
        if add_map_layer:
            QgsMapLayerRegistry.instance().addMapLayer(layer)

        __logger.info(u'Loading layer "{}" into QgsMapLayer.'.format(source))
    else:
        __logger.warn(u'Vector Layer "{}" is invalid to registry in QgsMapLayer.'.format(source))
    return layer


def raster_data_type(source, band=1):
    """
    Get raster type from source.

    Reference:

    How can I get multiple pixels from a raster based on a vector point file (https://gis.stackexchange.com/questions/123668/in-qgis-using-python-how-can-i-get-multiple-pixels-from-a-raster-based-on-a-vec)

    :param source: A string with raster path.
    :param band: A number with band.
    :return: A int with datatype (startswith 0) and a string with datatype name.
    """
    dataset = gdal.Open(source)
    raster_band = dataset.GetRasterBand(band)
    datatype = raster_band.DataType
    datatype_name = gdal.GetDataTypeName(datatype)

    del dataset
    return datatype, datatype_name


def vector_to_raster(layer, name_field, dimension, width, height, rtype, nodata,
                    compress_type, jpeg_compress_level, z_level, predictor,
                    tiled, bigtiff, extra, tfw, target_layer):
    """
    Uses GDAL Rasterize(apps/qgis/python/plugins/processing/algs/gdal/rasterize.py)

    :param layer: A layer with layer reference
    :param name_field: A string with atributte name of vector layer to make rasterize
    :param dimension: A integer with dimension with grid
    :param width: A integer with width pixel's size
    :param height: A integer with height pixel's size
    :param rtype: A integer with rtype
    :param nodata: A string with value of nodata
    :param compress_type: A integer with GeoTIFF options. Compression type
    :param jpeg_compress_level: A integer with JPEG compression level
    :param z_level: A integer with DEFLATE compression level
    :param predictor: A integer with LZW or DEFLATE compression
    :param tiled: A boolean with true to Create tiled output
    :param bigtiff: A integer with Control whether the created file is a BigTIFF or a classic TIFF
    :param extra: A string with extra parameters
    :param tfw: A boolean with true to Force the generation of an associated ESRI world file (.tfw)
    :param target_layer: A string with Target layer
    """

    ext = layer.extent()

    xmin = ext.xMinimum()
    xmax = ext.xMaximum()
    ymin = ext.yMinimum()
    ymax = ext.yMaximum()
    raster_extent = "%f,%f,%f,%f" %(xmin, xmax, ymin, ymax)

    src = layer.source()

    result = runalg(
        'gdalogr:rasterize',
        src,
        name_field,
        dimension,
        width,
        height,
        raster_extent,
        tfw,
        rtype,
        nodata,
        compress_type,
        jpeg_compress_level,
        z_level,
        predictor,
        tiled,
        bigtiff,
        extra,
        target_layer
    )

    source = result['OUTPUT']
    if source and os.path.isfile(source):
        return import_layer_qgis(source, suffix='rasterize', base_layer=src)
    else:
        raise IOError('Falha ao gerar arquivo resultante do processo de rasterize')


def clip_raster_by_mask(input_layer, mask_layer, output_layer, nodata='', add_alpha_band=False,
                        crop_to_cutline=False, keep_resolution=False, raster_type=5,
                        raster_compress_type=4, jpeg_compression=75, deflate_compression=6,
                        predictor=1, create_tiled=False, big_tiff=0, force_generate_tfw=False,
                        extra_params='', open_output_layer=False):
    """
    Uses GDAL clip by mask (apps/qgis/python/plugins/processing/algs/gdal/ClipByMask.py)

    :param input_layer: A string with Input layer
    :param mask_layer: A string with Mask layer
    :param output_layer: Input layer. None generate temp file
    :param nodata: Nodata value, leave blank to take the nodata value from input
    :param add_alpha_band: Create and output alpha band
    :param crop_to_cutline: Crop the extent of the target dataset to the extent of the cutline
    :param keep_resolution: Keep resolution of output raster
    :param raster_type: Output raster type: ['Byte', 'Int16', 'UInt16', 'UInt32', 'Int32', 'Float32', 'Float64']
    :param raster_compress_type: GeoTIFF options. Compression type: ['NONE', 'JPEG', 'LZW', 'PACKBITS', 'DEFLATE']
    :param jpeg_compression: Set the JPEG compression level 1, 100, 75.
    :param deflate_compression: Set the DEFLATE compression level: 1, 9, 6
    :param predictor: Set the predictor for LZW or DEFLATE compression: 1, 3, 1
    :param create_tiled: Create tiled output (only used for the GTiff format)
    :param big_tiff: Control whether the created file is a BigTIFF or a classic TIFF: ['', 'YES', 'NO', 'IF_NEEDED', 'IF_SAFER']
    :param force_generate_tfw: Force the generation of an associated ESRI world file (.tfw))
    :param extra_params: Additional creation parameters
    :param open_output_layer: Import layer created in Qgis
    :return: QgsRasterLayer
    """
    input_layer = unicode(input_layer)
    mask_layer = unicode(mask_layer)
    if output_layer is not None:
        output_layer = unicode(output_layer)

    result = runalg(
        'gdalogr:cliprasterbymasklayer',
        input_layer,
        mask_layer,
        nodata,
        add_alpha_band,
        crop_to_cutline,
        keep_resolution,
        raster_type,
        raster_compress_type,
        jpeg_compression,
        deflate_compression,
        predictor,
        create_tiled,
        big_tiff,
        force_generate_tfw,
        extra_params,
        output_layer
    )

    source = result['OUTPUT']
    if source and os.path.isfile(source):
        return import_layer_qgis(source, suffix='clipped', base_layer=input_layer, add_map_layer=open_output_layer)
    else:
        raise IOError(u'Falha ao gerar arquivo resultante do processo de clip: "{}"'.format(unicode(result)))


def raster_calculator(entries, base_layer, output_raster, expression, output_format='GTiff'):
    """
    Apply Qgis raster calculator.

    :param entries: A list of QgsRasterCalculatorEntry.
    :param base_layer: A QgsRasterLayer to extract the extent, width and height.
    :param output_raster: A string with the output path.
    :param expression: A string with the expression to be applied.
    :param output_format: The output format. Default GTiff.
    :return: A string with the output message.
    """
    output_msg = [
        'Calculation successful.',
        'Error creating output data file.',
        'Error reading input layer.'
        'User canceled calculation.',
        'Error parsing formula.'
        'Error allocating memory for result.'
        'Unknown error.'
    ]

    extent = base_layer.extent()
    width = base_layer.width()
    height = base_layer.height()

    try:
        __logger.debug(u'QgsRasterCalculator: expression "{}", output "{}", format "{}", width {}, height {}, {} entries'.format(
            expression,
            output_raster,
            output_format,
            str(width),
            str(height),
            str(len(entries))
        ))

        calc = QgsRasterCalculator(expression, output_raster, output_format, extent, width, height, entries)
        __logger.info('Applying model "propagacao"...')
        result = calc.processCalculation()
    except Exception as e:
        result = 6
        __logger.fatal('Fail to apply raster calculator: {}'.format(e.message))

    return result, output_msg[result]


def raster_calculator_from_config(qgs_raster_layers, expression_alias, expression_template, qgs_raster_base_layer, output_raster, band=1):
    """
    Apply raster calculator using layers name.

    :param qgs_raster_layers: A list with QgsRasterLayer.
    :param expression_alias: A list with expression alias. Example: ['v', 's', 'a', 'r', 'e'].
    :param expression_template: A string with expression template. Example: '1 + (100 * "{v}") + (30 * "{s}")+ (10 * "{a}") + (5 * "{r}") + (2 * "{e}")'.
    :param qgs_raster_base_layer: A QgsRasterLayer to extract geotransform.
    :param output_raster: A string with output raster path.
    :param band: A int with band number to perform raster calculator.
    :return: A string with status message.
    """
    if len(qgs_raster_layers) != len(expression_alias):
        raise ValueError(u'Layers count({}) differ from expression alias ({})'.format(len(qgs_raster_layers), len(expression_alias)))

    entries = []
    alias = {}
    elements_idx = 0

    if not qgs_raster_base_layer or not qgs_raster_base_layer.isValid():
        raise ValueError(u'Base layer "{}" does not exist or is not valid'.format(qgs_raster_base_layer))

    for layer in qgs_raster_layers:
        layer_name = layer.name()
        if not layer.isValid():
            result = 6
            msg = u'Layer "{}" not valid.'.format(layer_name)
            return result, msg
        else:
            ref = layer_name + unicode('@' + str(band))
            entry = QgsRasterCalculatorEntry()
            entry.ref = ref
            entry.raster = layer
            entry.bandNumber = band
            entries.append(entry)

            alias[expression_alias[elements_idx]] = ref
            elements_idx += 1

    expression = expression_template.format(**alias)
    __logger.info(u'Running raster calculator with expression: {}...'.format(expression))
    return raster_calculator(entries, qgs_raster_base_layer, output_raster, expression)


def set_layer_style(layer, plugin, style):
    """
    https://gis.stackexchange.com/questions/202230/loading-style-qml-file-to-layer-via-pyqgis
    https://qgis.org/api/classQgsMapLayer.html

    :param layer: A QgsMapLayer layer.
    :param plugin: A string with the name of plugin. Check cqfs.yaml.
    :param style: A string with the name of style. Check cqfs.yaml.
    :return: A boolean with success and a string with style name.
    """
    path = os.path.join(CQFS_STYLE, plugin, style + '.qml')
    if not os.path.isfile(path):
        __logger.fatal(u'Style "{}" does not exist.'.format(path))
        return False, None

    name, success = layer.loadNamedStyle(path)
    layer.triggerRepaint()
    return success, name


def point_to_path(input_layer, group, order, date, layer_output, txt_output):

    result = runalg(
        'qgis:pointstopath',
        input_layer,
        group,
        order,
        date,
        layer_output,
        txt_output,
    )

    source = result['OUTPUT_LINES']

    if source and os.path.isfile(source):
        return import_layer_qgis(source, suffix='line', base_layer=input_layer, is_vector=True)
    else:
        raise IOError(u'Falha ao gerar arquivo resultante do processo de gerar linha de transmissao')


def intersects(input_layer_line, input_layer_buffer, ignore_null, layer_output):

    result = runalg(
        'qgis:intersection',
        input_layer_line,
        input_layer_buffer,
        ignore_null,
        layer_output,
    )

    source = result['OUTPUT']

    if source and os.path.isfile(source):
        return import_layer_qgis(source, suffix='intersects', base_layer=input_layer_line, is_vector=True)
    else:
        raise IOError(u'Falha ao gerar arquivo resultante do processo de intersecção')


def has_attributes(layer, field):
    index = layer.fieldNameIndex(field)
    if index == -1:
        return False
    else:
        return True


def clip(input_layer, buffer_layer, output_layer):
    result = runalg(
        'qgis:clip',
        input_layer,
        buffer_layer,
        output_layer
    )

    source = result['OUTPUT']
    if source and os.path.isfile(source):
        return import_layer_qgis(source, suffix='clipped', base_layer=input_layer)
    else:
        raise IOError(u'Falha ao gerar arquivo resultante do processo de clip')


def buffer_by_column(input_layer, attribute, scaling, max_distance, straight_corners, caps_ends, vectors,
                     tolerance, min_area, output_type, output):

    result = runalg(
        'grass7:v.buffer.column',
        input_layer,
        attribute,
        scaling,
        max_distance,
        straight_corners,
        caps_ends,
        vectors,
        tolerance,
        min_area,
        output_type,
        output
    )

    source = result['output']

    if source and os.path.isfile(source):

        return import_layer_qgis(source, suffix='buffer', base_layer=input_layer, is_vector=True)
    else:
        raise IOError(u'Falha ao gerar arquivo resultante do processo de gerar linha de transmissao')


def save_file(layer, output):
    provider = layer.dataProvider()
    writer = QgsVectorFileWriter.writeAsVectorFormat(layer, output, provider.encoding(),  provider.crs())

    return writer


def validate_fields(layer, attributes):
    """
    Check if a layer contains all necessary attributes.

    :param layer: A QgsVectorLayer.
    :param attributes: A list of string with mandatories attributes.
    :return: A list of errors.
    """
    errors = []

    field_names = [unicode(field.name()).lower() for field in layer.pendingFields()]
    field_names.sort()

    name = layer.name()
    for attr in attributes:
        if attr not in field_names:
            errors.append(u'Layer "{}" does not have attribute "{}"'.format(name, attr))

    return errors


def remove_layers(layers):
    QgsMapLayerRegistry.instance().removeMapLayers(layers)

