# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-10-11
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
import os
import yaml
import traceback

from ..handler import Handler
from ....src.handler.shared.validate_layer_handler import ValidateVectorHandler
from model_handler import ModelHandler


class FormulaHandler(Handler):

    def handle(self, **kwargs):
        cqfs = kwargs['cqfs']

        handler_2 = ModelHandler(successor=None)
        handler_1 = ValidateVectorHandler(successor=handler_2)

        try:
            weight_path = cqfs.dlg.ignicao_line_entrada_formula.text()
            if not os.path.isfile(weight_path):
                raise RuntimeError('Weight file is mandatory.')

            with open(weight_path, 'r') as stream:
                weight = yaml.load(stream)

                if weight is None or len(weight) == 0:
                    raise RuntimeError('Fail to load weight file.')

                kwargs['weight'] = weight
                handler_1.handle(**kwargs)
        except Exception as e:
            error_msg = u'{} => {}'.format(unicode(e), unicode(traceback.format_exc()))
            self.logger.fatal(error_msg)
            cqfs.show_error(error_msg)
