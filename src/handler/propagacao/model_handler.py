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


class ModelHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 8...')

        propagacao = kwargs['objeto']
        reclass_layers = kwargs['reclass_layers']
        output_raster = kwargs['output_layer']

        code, msg = propagacao.apply_model(
            reclass_layers['vegetacao'],
            reclass_layers['clinografia'],
            reclass_layers['orientacao_vertente'],
            reclass_layers['proximidade_estradas'],
            reclass_layers['hipsometria'],
            output_raster
        )

        if code == 0:
            self.info = msg
            self.next(**kwargs)
        else:
            self.error = msg
            raise RuntimeError(self.error)
