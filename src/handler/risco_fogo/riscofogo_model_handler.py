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
from re import findall
from ..handler import Handler
from ....src.constants import PLUGIN_RISCO_FOGO
from ....src.cqfs_config import load_config
from ....src.layer_util import raster_calculator_from_config, import_layer_qgis, set_layer_style, remove_layers

cqfs_config = load_config()
proj4 = cqfs_config['global']['crs_proj4']


class RiscoFogoModelHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 6...')
        
        expression_template = cqfs_config['riscofogo']['expression']
        default_band = cqfs_config['riscofogo']['expression_default_band']
        expression_base_layer = cqfs_config['riscofogo']['expression_base_layer']

        qgs_raster_layers = [kwargs['rasterize_vector_layer'], kwargs['raster_out_normalize']]
        expression_alias = findall(r'\{(.*?)\}', expression_template)

        idx = expression_alias.index(expression_base_layer)
        qgs_raster_base_layer = qgs_raster_layers[idx]
        output_raster = kwargs['output_layer']

        code, msg = raster_calculator_from_config(qgs_raster_layers, expression_alias, expression_template, qgs_raster_base_layer, output_raster, default_band)
        if code == 0:
            self.info = msg

            layers = [kwargs['raster_out_normalize'], kwargs['rasterize_vector_layer']]
            remove_layers(layers)

            layer = import_layer_qgis(output_raster)
            set_layer_style(layer, PLUGIN_RISCO_FOGO, PLUGIN_RISCO_FOGO)

            self.next(**kwargs)
        else:
            self.error = msg
            raise RuntimeError(self.error)
