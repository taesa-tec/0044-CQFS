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


class RiscoFogoNormalizacaoReclass(Reclass):

    DATA_TYPE = gdal.GDT_Float64

    def __init__(self, input_raster, output_raster):
        super(RiscoFogoNormalizacaoReclass, self).__init__(input_raster, output_raster, datatype=self.DATA_TYPE)

    def normalize(self,list_normal,nodata):
        max_value  = np.max(list_normal)
        new_nodata = max_value + 400 # 400 é um número qualquer, utilizado apenas para garantir que o nodata será menor que 0
        list_normal[list_normal == nodata] = new_nodata
        
        min_value = np.min(list_normal)
        
        list_normal =   1 - ((list_normal - min_value) / (max_value - min_value))

        list_normal[list_normal < 0] = nodata
        
        return list_normal

    def apply(self, array, nodata):
        return self.normalize(array,nodata)

