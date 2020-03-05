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


class ZonalHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 4...')

        criticidade = kwargs['objeto']
        output_criticidade = kwargs['output_criticidade_vector']
        vao_layer = kwargs['vao_layer']
        risco_fogo_layer = kwargs['rasters_selected'][0]

        self.logger.debug('risco_fogo_layer')
        self.logger.debug(risco_fogo_layer)

        error, zonal_layer = criticidade.generate_zonal(vao_layer, risco_fogo_layer, output_criticidade)
        if not error:
            kwargs['zonal_layer'] = zonal_layer
            self.next(**kwargs)
        else:
            self.error = error
            self.logger.error(error)
            raise RuntimeError(self.error)


