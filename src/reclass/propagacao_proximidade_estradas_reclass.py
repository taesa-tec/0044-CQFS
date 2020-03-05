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
from osgeo import gdal
from reclass import Reclass


class PropagacaoProximidadeEstradasReclass(Reclass):

    DATA_TYPE = gdal.GDT_Int32

    def __init__(self, input_raster, output_raster):
        super(PropagacaoProximidadeEstradasReclass, self).__init__(input_raster, output_raster, datatype=self.DATA_TYPE)

    def apply(self, array, nodata):
        return array
