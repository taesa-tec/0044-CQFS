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
from ....src.layer_util import save_file, remove_layers
from ..handler import Handler


class SaveFileHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 9...')

        vulnerabilidade_layer = kwargs['buffer_line_layer']
        output_vector = kwargs['output_vector']

        try:
            save_file(vulnerabilidade_layer, output_vector)
            self.next(**kwargs)

        except Exception as e:
            raise RuntimeError(str(e))


class RemoveLayersHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 9...')
        layers = [kwargs['line_layer'], kwargs['buffer_layer'], kwargs['buffer_pc_layer'], kwargs['intersects_layer'],
                  kwargs['buffer_line_layer'], kwargs['clip_line_layers']]

        try:
            remove_layers(layers)

            self.logger.debug('>>> Fim Handler 9')

            self.next(**kwargs)

        except Exception as e:
            raise RuntimeError(str(e))
