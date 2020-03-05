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
from qgis._core import QgsVectorLayer, QgsMapLayerRegistry
from ....src.constants import PLUGIN_CRITICIDADE
from ....src.cqfs_config import load_config

from ....src.layer_util import save_file, remove_layers, set_layer_style
from ..handler import Handler


class SaveFileHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 7...')
        __config = load_config()
        params = __config[PLUGIN_CRITICIDADE]

        criticidade_layer = kwargs['criticidade_layer']
        output_vector = kwargs['output_criticidade_vector']

        try:
            save_file(criticidade_layer, output_vector)

            layers = [kwargs['criticidade_layer']]
            remove_layers(layers)

            output_layer = QgsVectorLayer(output_vector, 'criticidade', 'ogr')
            QgsMapLayerRegistry.instance().addMapLayers([output_layer])

            style = params['style']
            set_layer_style(output_layer, PLUGIN_CRITICIDADE, style['criticidade'])

            self.next(**kwargs)

        except Exception as e:
            raise RuntimeError(str(e))

