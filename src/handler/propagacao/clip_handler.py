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
from ....src.spatial_operations import clip_rasters as sp_clip_rasters


class ClipHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 6...')

        buffer_layer = kwargs['buffer_layer']
        raster_layers = kwargs['raster_layers']

        clip_success, clip_layers = sp_clip_rasters(buffer_layer, raster_layers)
        if clip_success:
            kwargs['clip_layers'] = clip_layers
            self.next(**kwargs)
        else:
            self.error = 'Fail to clip layers.'
            self.logger.fatal(self.error)
            raise RuntimeError(self.error)
