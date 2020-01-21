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
from ...handler.handler import Handler
from ....src.plugin_util import validate_vectors, validate_rasters
from ....src.cqfs_config import load_config

cqfs_config = load_config()
proj4 = cqfs_config['global']['crs_proj4']


class ValidateVectorHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 2...')

        layers = kwargs['layers']
        combo_vector = kwargs['combo_vector']

        msgselecione = 'Selecione a linha de transmissao.',
        msgprojecao = 'Linha de transmissao nao possui projecao experada "{}".'

        if 'msgselecione' in kwargs:
            msgselecione = kwargs['msgselecione']

        if 'msgprojecao' in kwargs:
            msgprojecao = kwargs['msgprojecao']

        vector_error, vector_layer = validate_vectors(layers, combo_vector, proj4, msgselecione, msgprojecao)
        if not vector_error:
            kwargs['vector_layer'] = vector_layer
            self.next(**kwargs)
        else:
            self.error = vector_error
            self.logger.error(vector_error)
            raise RuntimeError(self.error)


class ValidateRasterHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 3...')

        layers = kwargs['layers']
        rasters_name = kwargs['rasters_name']
        objeto = kwargs['objeto']

        error_msg, rasters_selected = validate_rasters(objeto, layers, rasters_name, proj4)
        if not error_msg:
            kwargs['rasters_selected'] = rasters_selected
            self.next(**kwargs)
        else:
            self.error = error_msg
            self.logger.error(error_msg)
            raise RuntimeError(self.error)
