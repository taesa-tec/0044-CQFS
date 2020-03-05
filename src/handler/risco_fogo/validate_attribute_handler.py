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
from ....src.layer_util import validate_fields
from ..handler import Handler
from ....src.cqfs_config import load_config

cqfs_config = load_config()


class ValidateVectorAttributeHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 6...')
        
        attributes = [cqfs_config['riscofogo']['attr_equacao']]
        vector_layer = kwargs['vector_layer']

        error = validate_fields(vector_layer, attributes)
        if len(error) == 0:
            self.next(**kwargs)
        else:
            self.error = u', '.join(error)
            raise RuntimeError(self.error)
