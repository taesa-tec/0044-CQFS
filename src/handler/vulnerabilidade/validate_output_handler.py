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


class ValidateOutputHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 1...')

        line_saida_vulnerabilidade = kwargs['line_saida_vulnerabilidade']
        output_vector = line_saida_vulnerabilidade.text()

        is_output_valid = output_vector and len(output_vector) > 0
        if is_output_valid:
            kwargs['output_vector'] = output_vector
            self.next(**kwargs)
        else:
            self.error = 'Selecione o arquivo de saida!'
            self.logger.error(self.error)
            raise RuntimeError(self.error)
