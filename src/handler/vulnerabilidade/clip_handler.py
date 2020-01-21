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
from ....src.constants import PLUGIN_VULNERABILIDADE

from ..handler import Handler
from ....src.spatial_operations import clip_vectors


class ClipHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 7...')

        vao_layer = kwargs['vao_layer']
        line_layers = kwargs['intersects_layer']

        clip_success, clip_layers = clip_vectors(vao_layer, line_layers, PLUGIN_VULNERABILIDADE)
        if clip_success:
            kwargs['clip_line_layers'] = clip_layers
            self.next(**kwargs)
        else:
            self.error = 'Fail to clip layers.'
            self.logger.fatal(self.error)
            raise RuntimeError(self.error)
