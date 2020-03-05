# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-09-18
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
import numpy as np
from osgeo import gdal
from reclass import Reclass


class PropagacaoVegetacaoReclass(Reclass):

    DATA_TYPE = gdal.GDT_Float32

    def __init__(self, input_raster, output_raster):
        super(PropagacaoVegetacaoReclass, self).__init__(input_raster, output_raster, datatype=self.DATA_TYPE)

    def apply(self, array, nodata):
        float_array = array.astype(np.float32)

        float_array[float_array == float(nodata)] = float(nodata)

        float_array[float_array == 1.0] = 0.5
        float_array[float_array == 2.0] = 1
        float_array[float_array == 3.0] = 0
        float_array[float_array == 4.0] = 0
        float_array[float_array == 5.0] = 0
        float_array[float_array == 6.0] = 1
        float_array[float_array == 7.0] = 1
        float_array[float_array == 8.0] = 1.5
        float_array[float_array == 9.0] = 1
        float_array[float_array == 10.0] = 1
        float_array[float_array == 11.0] = 1
        float_array[float_array == 12.0] = 0.5
        float_array[float_array == 13.0] = 3
        float_array[float_array == 14.0] = 3
        float_array[float_array == 15.0] = 1.5
        float_array[float_array == 16.0] = 0.5
        float_array[float_array == 17.0] = 0.5
        float_array[float_array == 18.0] = 0
        float_array[float_array == 19.0] = 3
        float_array[float_array == 20.0] = 2
        float_array[float_array == 21.0] = 2
        float_array[float_array == 22.0] = 1.5
        return float_array
