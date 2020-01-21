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
from ....src.calc_operations import classificar_criticidade

from ....src.constants import PLUGIN_CRITICIDADE, PLUGIN_VULNERABILIDADE

from ..handler import Handler


class ClassifyRiscoHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 5...')

        criticidade = kwargs['objeto']
        zonal_layer = kwargs['zonal_layer']

        error, zonal_layer = criticidade.classify_risco(zonal_layer)
        if not error:
            kwargs['zonal_layer'] = zonal_layer
            self.next(**kwargs)
        else:
            self.error = error
            self.logger.error(error)
            raise RuntimeError(self.error)


class ClassifyCriticidadeHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 6...')

        zonal_layer = kwargs['zonal_layer']
        vulnerabilidade_layer = kwargs['vao_layer']

        error, criticidade_layer = classificar_criticidade(zonal_layer, vulnerabilidade_layer, PLUGIN_CRITICIDADE, PLUGIN_VULNERABILIDADE)
        if not error:
            kwargs['criticidade_layer'] = criticidade_layer
            self.next(**kwargs)
        else:
            self.error = error
            self.logger.error(error)
            raise RuntimeError(self.error)
