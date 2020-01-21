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


class ValidateVectorHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 2...')

        layers = kwargs['layers']
        vulnerabilidade = kwargs['vulnerabilidade']
        combo_vao = kwargs['combo_vao']
        combo_ponto_critico = kwargs['combo_ponto_critico']
        combo_torres = kwargs['combo_torres']

        error, vao_layer, pc_layer, torres_layer = vulnerabilidade.validate(layers, combo_vao, combo_ponto_critico, combo_torres)
        if not error:
            kwargs['vao_layer'] = vao_layer
            kwargs['pc_layer'] = pc_layer
            kwargs['torres_layer'] = torres_layer
            self.next(**kwargs)
        else:
            self.error = error
            self.logger.error(error)
            raise RuntimeError(self.error)


