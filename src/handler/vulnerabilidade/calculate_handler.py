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
from processing.core.SilentProgress import SilentProgress
from ....src.calc_operations import calc

from ..handler import Handler
from ....src.constants import PLUGIN_VULNERABILIDADE


class CalculateHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 4...')

        self.logger.debug(kwargs)

        vao_layer = kwargs['vao_layer']

        if vao_layer:
            buffer_layer = calc(PLUGIN_VULNERABILIDADE, SilentProgress(), vao_layer)
            kwargs['buffer_layer'] = buffer_layer
            self.next(**kwargs)

