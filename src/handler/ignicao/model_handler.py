# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-10-10
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
from ....src.layer_util import validate_fields, set_layer_style
from ....src.constants import PLUGIN_IGNICAO


class ModelHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 1...')

        cqfs = kwargs['cqfs']
        ignicao = cqfs.ignicao

        grid = kwargs['vector_layer']
        weight = kwargs['weight']

        errors = []
        success = True

        if grid is not None:
            if not weight or len(weight) == 0:
                errors.append('File of equation weight is undefined.')

            attributes = ignicao.params['grid_attributes']
            missing_fields = validate_fields(grid, attributes)

            errors.extend(missing_fields)
            if len(errors) > 0:
                success = False
            else:
                ignicao.apply_model(grid, weight)
        else:
            errors.append('Grid is undefined.')
            success = False

        if success:
            set_layer_style(grid, PLUGIN_IGNICAO, PLUGIN_IGNICAO)
            self.next(**kwargs)
        else:
            self.error = ', '.join(errors)
            self.logger.fatal(self.error)
            raise RuntimeError(self.error)
