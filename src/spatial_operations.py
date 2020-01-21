# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-09-21
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
import os
import logging
import traceback

from math import ceil, isnan, isinf
from qgis.core import QGis, QgsFeature, QgsVectorLayer
from qgis.core import QgsMapLayerRegistry
from cqfs_config import load_config, tmp_filename_without_extension
from layer_util import clip_raster_by_mask, intersects, buffer_by_column, set_layer_style
from layer_util import is_vector_layer
from layer_util import point_to_path
from layer_util import raster_data_type
from processing.algs.qgis import Buffer as buff
from processing.tools.vector import VectorWriter
from qt_handler import QtHandler

from osgeo import ogr, osr

__logger = logging.getLogger('spatial_operations')
__config = load_config()

__OGR_DRIVER_NAME = 'ESRI Shapefile'


def buffering(plugin_name, progress, layer, destination='memory:', open_output_layer=True):
    dlg, bar = QtHandler.progress_dialog(label='Buffering...')

    name = layer.name()
    __logger.info(u'Buffering layer "{}"...'.format(name))

    if not is_vector_layer(layer):
        __logger.warn(u'Layer "{}" is not QVectorLayer, got layer type {}'.format(name, layer.type()))
        return

    bar.setValue(10)

    writer = VectorWriter(destination, None, layer.pendingFields().toList(), QGis.WKBPolygon, layer.crs(), None)

    bar.setValue(20)

    params = __config[plugin_name]
    __logger.info(u'Running buffering algorithm for "{}"...'.format(destination))
    __logger.info(params['dissolve'])
    buff.buffering(progress, writer, params['distance'], None, False, layer, params['dissolve'], params['segments'])

    bar.setValue(60)

    output = writer.layer
    output_layer_name = u'{}_buffer'.format(name)
    if output:
        output.setName(output_layer_name)
    else:
        output = QgsVectorLayer(destination, output_layer_name, 'ogr')

    bar.setValue(80)

    if output.isValid():
        if open_output_layer:
            QgsMapLayerRegistry.instance().addMapLayers([output])
        __logger.info(u'Buffer created with success.')
    else:
        __logger.fatal(u'Layer created is invalid.')

    bar.setValue(100)
    bar.close()
    dlg.close()
    del dlg

    return output


def clip_rasters(buffer_layer, raster_layers):
    success = True
    tempfile = None
    new_layers = []
    buffer_source = buffer_layer.source()

    current = 0
    last_progress = 0
    size = len(raster_layers)
    total = 100 / size if size > 0 else 1
    dlg, bar = QtHandler.progress_dialog(label='Clipping rasters...')

    __logger.info(u'Clip {} rasters with buffer "{}"'.format(str(size), buffer_layer.name()))
    for layer in raster_layers:
        name = layer.name()
        source = layer.source()
        datatype, datatype_name = raster_data_type(source)
        datatype = datatype - 1

        __logger.info(u'Clipping raster "{}" with source "{}", datatype: "{}" and datatype_name: "{}"...'.format(name, source, str(datatype), str(datatype_name)))

        try:
            output = clip_raster_by_mask(source, buffer_source, tempfile, raster_type=datatype)
            new_layers.append(output)
        except Exception as e:
            success = False
            __logger.fatal(u'Fail to clip raster "{}": {} => {}'.format(name, e.message, str(traceback.format_exc())))

        current += 1
        percentage = int(current * total)
        __logger.info(u'Clipping status: {}%...'.format(str(percentage)))
        bar.setValue(percentage)
        last_progress = percentage

    if last_progress < 100:
        bar.setValue(100)

    bar.close()
    dlg.close()
    del dlg

    if success:
        __logger.info(u'All rasters clipped successfully.')

    return success, new_layers


def create_line(plugin_name, progress, layer):
    dlg, bar = QtHandler.progress_dialog(label='Creating line...')

    params = __config[plugin_name]

    tempfile = tmp_filename_without_extension()
    layer_source = layer.source()

    bar.setValue(20)
    try:
        output = point_to_path(layer_source, params['att_grupo'], params['att_vao_id'], '', tempfile, None)
        bar.setValue(80)

    except Exception as e:
        __logger.fatal(u'Fail to convert point to path: {}'.format(str(e)))
        raise RuntimeError(str(e))

    bar.setValue(100)

    bar.close()
    dlg.close()
    del dlg

    __logger.info(u'Line created successfully.')
    return output


def intersect(plugin_name, progress, line_layer, buffer_pc_layer):
    dlg, bar = QtHandler.progress_dialog(label='Creating Intersection...')
    tempfile = tmp_filename_without_extension()

    bar.setValue(20)

    line_layer_source = line_layer.source()
    buffer_pc_layer_source = buffer_pc_layer.source()

    bar.setValue(40)

    try:
        output = intersects(line_layer_source, buffer_pc_layer_source, True, tempfile)
        bar.setValue(80)

    except Exception as e:
        __logger.fatal(u'Fail to intersects buffer with line: {}'.format(str(e)))
        raise RuntimeError(str(e))

    bar.setValue(100)

    bar.close()
    dlg.close()
    del dlg

    __logger.info(u'Intersection created successfully.')
    return output


def clip_vectors(vao_layer, line_layer, plugin_name):
    dlg, bar = QtHandler.progress_dialog(label='Clipping Vectors...')

    params = __config[plugin_name]
    success = True
    new_features = []
    lines = {}

    bar.setValue(20)

    writer = VectorWriter('memory:', None, vao_layer.pendingFields().toList(), QGis.WKBLineString, vao_layer.crs(), None)
    vl = writer.layer
    pr = writer.writer

    bar.setValue(30)

    vl.startEditing()
    for feat_line in line_layer.getFeatures():
        key = int(feat_line[params['att_line_id']])
        lines[key] = feat_line

    bar.setValue(40)

    for feat_vao in vao_layer.getFeatures():
        idx = feat_vao.fieldNameIndex(params['att_vao_id'])
        attr = int(feat_vao.attributes()[idx])

        attributes = feat_vao.attributes()

        try:
            line = lines[attr]
            geom = feat_vao.geometry()
            geom_line = line.geometry()
            fet = QgsFeature()
            fet.setGeometry(geom.intersection(geom_line))
            fet.setAttributes(attributes)
            new_features.append(fet)
        except Exception as e:
            __logger.error(str(e))

    bar.setValue(80)

    pr.addFeatures(new_features)
    vl.updateFields()
    vl.commitChanges()

    if len(new_features) > 0:
        QgsMapLayerRegistry.instance().addMapLayer(vl)

    bar.setValue(100)

    bar.close()
    dlg.close()
    del dlg

    __logger.info(u'All vectors clipped successfully.')
    return success, vl


def buffer_line(plugin_name, progress, layer, output):
    dlg, bar = QtHandler.progress_dialog(label='Buffering Line...')

    layer_source = layer.source()

    bar.setValue(20)

    params = __config[plugin_name]

    extent = layer.extent()
    xmin = extent.xMinimum()
    xmax = extent.xMaximum()
    ymin = extent.yMinimum()
    ymax = extent.yMaximum()

    vector = str(xmin) + ',' + str(xmax) + ',' + str(ymin) + ',' + str(ymax)

    bar.setValue(40)

    try:
        output_temp = buffer_by_column(layer_source, params['att_buffer_dist'], params['scale'], params['max_distance'],
                                  params['straight_corners'], params['caps_ends'], vector, params['tolerance'],
                                  params['min_area'], params['output_type'], output)
        bar.setValue(80)

    except Exception as e:
        __logger.fatal(u'Fail to create buffer: {}'.format(str(e)))
        raise RuntimeError(str(e))

    output_layer = QgsVectorLayer(output, 'area_manutencao', 'ogr')
    QgsMapLayerRegistry.instance().addMapLayers([output_layer])

    style = params['style']
    set_layer_style(output_layer, plugin_name, style['faixa_manutencao'])

    bar.setValue(100)

    bar.close()
    dlg.close()
    del dlg

    __logger.info(u'Buffer created successfully.')
    return output_temp


def create_grid(input_gridfn, output_gridfn, xmin, xmax, ymin, ymax, grid_height, grid_width):
    """

    Creates a grid using a buffer. This method uses pure GDAL python.

    :param input_gridfn: A string with base buffer source.
    :param output_gridfn: A string with output source.
    :param xmin: float
    :param xmax: float
    :param ymin: float
    :param ymax: float
    :param grid_height: Cell size
    :param grid_width: Cell size
    :return: void
    """
    xmin = float(xmin)
    xmax = float(xmax)
    ymin = float(ymin)
    ymax = float(ymax)
    grid_width = float(grid_width)
    grid_height = float(grid_height)

    assert (not isnan(xmin)) and (not isinf(xmin))
    assert (not isnan(xmax)) and (not isinf(xmax))
    assert (not isnan(ymin)) and (not isinf(ymin))
    assert (not isnan(ymax)) and (not isinf(ymax))
    assert (not isnan(grid_width)) and (not isinf(grid_width))
    assert (not isnan(grid_height)) and (not isinf(grid_height))

    if not os.path.isfile(input_gridfn):
        raise RuntimeError(u'Base layer does not exist in filesystem, got "{}".'.format(input_gridfn))

    # get rows
    rows = ceil((ymax - ymin) / grid_height)
    # get columns
    cols = ceil((xmax - xmin) / grid_width)

    label = u'Creating a grid with {} rows and {} cols ({} cells)...'.format(rows, cols, rows * cols)
    __logger.info(label)

    dlg, bar = QtHandler.progress_dialog(label=label)

    # start grid cell envelope
    ring_xleft_origin = xmin
    ring_xright_origin = xmin + grid_width
    ring_ytop_origin = ymax
    ring_ybottom_origin = ymax - grid_height

    # create output file
    if os.path.exists(output_gridfn):
        os.remove(output_gridfn)

    ogr_driver = ogr.GetDriverByName(__OGR_DRIVER_NAME)

    base_data_source = ogr.Open(input_gridfn, 0)
    if not base_data_source:
        raise RuntimeError(u'Fail to open base layer "{}".'.format(input_gridfn))

    bbox_layer = base_data_source.GetLayer()
    bbox_feature = bbox_layer.GetNextFeature()
    bbox_geom = bbox_feature.GetGeometryRef()
    bbox_srs = bbox_layer.GetSpatialRef()

    out_data_source = ogr_driver.CreateDataSource(output_gridfn)
    out_layer = out_data_source.CreateLayer(output_gridfn, bbox_srs, ogr.wkbPolygon)
    feature_defn = out_layer.GetLayerDefn()

    current = 0
    last_progress = 0
    total = 100.0 / cols if cols > 0 else 1

    # create grid cells
    countcols = 0
    while countcols < cols:
        countcols += 1

        # reset envelope for rows
        ring_ytop = ring_ytop_origin
        ring_ybottom = ring_ybottom_origin

        countrows = 0
        while countrows < rows:
            countrows += 1

            geom = __create_polygon(ring_xleft_origin, ring_xright_origin, ring_ybottom, ring_ytop)

            if geom.Intersects(bbox_geom):
                # add new geom to layer
                __add_geom_to_layer(feature_defn, out_layer, geom)

            # new envelope for next geom
            ring_ytop = ring_ytop - grid_height
            ring_ybottom = ring_ybottom - grid_height

        # new envelope for next geom
        ring_xleft_origin = ring_xleft_origin + grid_width
        ring_xright_origin = ring_xright_origin + grid_width

        current += 1
        progress = int(current * total)
        if progress != last_progress and progress % 10 == 0:
            __logger.info('Grid status: {}%...'.format(str(progress)))
            bar.setValue(progress)
        last_progress = progress

    # Save and close DataSources
    del feature_defn
    del out_layer
    del out_data_source
    del bbox_feature
    del bbox_layer
    del base_data_source

    if last_progress < 100:
        bar.setValue(100)

    bar.close()
    dlg.close()
    del dlg


def __add_geom_to_layer(feature_defn, out_layer, poly):
    out_feature = ogr.Feature(feature_defn)
    out_feature.SetGeometry(poly)
    out_layer.CreateFeature(out_feature)
    del out_feature


def __create_polygon(ring_xleft_origin, ring_xright_origin, ring_ybottom, ring_ytop):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(ring_xleft_origin, ring_ytop)
    ring.AddPoint(ring_xright_origin, ring_ytop)
    ring.AddPoint(ring_xright_origin, ring_ybottom)
    ring.AddPoint(ring_xleft_origin, ring_ybottom)
    ring.AddPoint(ring_xleft_origin, ring_ytop)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    return poly
