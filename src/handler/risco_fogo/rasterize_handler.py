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
from ..handler import Handler
from ....src.layer_util import vector_to_raster


class RasterizeHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 5...')

        if 'vector_layer' not in kwargs:
            self.error = 'Selecione o vetor para conversao'
            self.logger.error(self.error)
            raise RuntimeError(self.error)
        
        else:
            vector_layer = kwargs['vector_layer']

            kwargs['rasterize_vector_layer'] = vector_to_raster(vector_layer, "Equacao", 1, 30, 30, 5, "-9999",
                              4, 75, 6, 1, False, 0, '', False, None)
            
            self.next(**kwargs)