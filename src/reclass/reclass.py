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
from osgeo import gdal


class Reclass(object):
    """
    An interface common to all supported algorithms.
    """

    def __init__(self, input_raster, output_raster, nodata=None, datatype=gdal.GDT_Float32):
        self.input_raster = input_raster
        self.output_raster = output_raster
        self.nodata = nodata
        self.datatype = datatype

    def apply(self, array, nodata):
        pass
