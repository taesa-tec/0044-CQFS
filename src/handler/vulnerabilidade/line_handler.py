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
from ....src.spatial_operations import intersect

from ....src.spatial_operations import create_line

from ..handler import Handler
from ....src.constants import PLUGIN_VULNERABILIDADE


class CreateLineHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 3...')

        torre_layer = kwargs['torres_layer']

        if torre_layer:
            line_layer = create_line(PLUGIN_VULNERABILIDADE, SilentProgress(), torre_layer)
            kwargs['line_layer'] = line_layer
            self.next(**kwargs)


class CreateLinePCHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 6...')

        line_layer = kwargs['line_layer']
        buffer_pc_layer = kwargs['buffer_pc_layer']

        if line_layer and buffer_pc_layer:
            intersects_layer = intersect(PLUGIN_VULNERABILIDADE, SilentProgress(), line_layer, buffer_pc_layer)
            kwargs['intersects_layer'] = intersects_layer
            self.next(**kwargs)
