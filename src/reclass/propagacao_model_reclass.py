# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-09-19
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
from reclass import Reclass


class PropagacaoModelReclass(Reclass):

    DEFAULT_NODATA = -9999.0
    MAX_MODEL_VALUE = 295
    DATA_TYPE = gdal.GDT_Float32

    def __init__(self, input_raster, output_raster):
        super(PropagacaoModelReclass, self).__init__(input_raster, output_raster, self.DEFAULT_NODATA, self.DATA_TYPE)

    def apply(self, array, base_raster_nodata):
        array[array == base_raster_nodata] = self.DEFAULT_NODATA
        array[array >= 300] = self.MAX_MODEL_VALUE
        return array
