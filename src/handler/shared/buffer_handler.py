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
from qgis.core import QgsMapLayer

from processing.core.SilentProgress import SilentProgress
from ....src.spatial_operations import buffering as sp_buffering
from ....src.layer_util import layers_by_type, buffer_within_rasters

from ....src.handler.handler import Handler


class CreateBufferHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 4...')

        vector_layer = kwargs['vector_layer']
        plugin_name = kwargs['plugin_name']

        if vector_layer:
            destination = 'memory:' if 'buffer_source' not in kwargs else kwargs['buffer_source']
            open_output_layer = True if 'open_output_layer' not in kwargs else kwargs['open_output_layer']

            buffer_layer = sp_buffering(plugin_name, SilentProgress(), vector_layer, destination=destination, open_output_layer=open_output_layer)
            if buffer_layer and buffer_layer.isValid():
                kwargs['buffer_layer'] = buffer_layer
                self.next(**kwargs)
            else:
                self.error = 'Fail to create buffer, buffer is null or feature count is zero.'
                self.logger.fatal(self.error)
                raise RuntimeError(self.error)
        else:
            self.error = 'Failt to get grid layer.'
            self.logger.fatal(self.error)
            raise RuntimeError(self.error)


class ValidateRasterWithBufferHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 5...')

        layers = kwargs['layers']
        buffer_layer = kwargs['buffer_layer']
        rasters_selected = kwargs['rasters_selected']

        if len(rasters_selected) == 0:
            raise RuntimeError('No rasters selected to validate buffer.')

        within_success, within_errors = buffer_within_rasters(buffer_layer, rasters_selected)

        if within_success:
            kwargs['raster_layers'] = rasters_selected
            self.next(**kwargs)
        else:
            self.error = ', '.join(within_errors)
            self.logger.fatal(self.error)
            raise RuntimeError(self.error)

