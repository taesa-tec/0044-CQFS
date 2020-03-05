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

from ....src.spatial_operations import buffering as sp_buffering, buffer_line
from ....src.layer_util import layers_by_type, buffer_within_rasters

from ..handler import Handler
from ....src.constants import PLUGIN_VULNERABILIDADE


class CreateBufferPCHandler(Handler):

    def handle(self, **kwargs):
        self.logger.error('>>> Handler: 5...')

        pc_layer = kwargs['pc_layer']

        if pc_layer:
            buffer_pc_layer = sp_buffering(PLUGIN_VULNERABILIDADE, SilentProgress(), pc_layer)
            kwargs['buffer_pc_layer'] = buffer_pc_layer
            self.next(**kwargs)


class CreateBufferHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 4...')

        self.logger.debug(kwargs['line_layer'])

        line_layer = kwargs['clip_line_layers']

        if line_layer:
            buffer_layer = sp_buffering(PLUGIN_VULNERABILIDADE, SilentProgress(), line_layer)
            kwargs['buffer_clip_layer'] = buffer_layer
            self.next(**kwargs)


class BufferClipHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 8...')

        self.logger.debug(kwargs['clip_line_layers'])

        line_layer = kwargs['clip_line_layers']
        output_vector = kwargs['output_vector']

        if line_layer:
            buffer_layer = buffer_line(PLUGIN_VULNERABILIDADE, SilentProgress(), line_layer, output_vector)
            kwargs['buffer_line_layer'] = buffer_layer
            self.next(**kwargs)


class CreateBufferByPointsHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 5...')

        torre_layer = kwargs['torre_layer']

        if torre_layer:
            buffer_layer = sp_buffering(PLUGIN_VULNERABILIDADE, SilentProgress(), torre_layer)
            kwargs['buffer_layer_teste'] = buffer_layer
            self.next(**kwargs)
