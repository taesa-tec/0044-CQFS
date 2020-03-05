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
from handler import Handler
from criticidade.validate_output_handler import ValidateOutputHandler
from criticidade.validate_layer_handler import ValidateVectorHandler
from shared.validate_layer_handler import ValidateRasterHandler
from criticidade.zonal_handler import ZonalHandler
from criticidade.classify_handler import ClassifyRiscoHandler, ClassifyCriticidadeHandler
from criticidade.save_file_handler import SaveFileHandler


class CriticidadeHandler(Handler):

    def handle(self, **kwargs):

        self.logger.error('>>> CriticidadeHandler')

        handler_7 = SaveFileHandler(successor=None)
        handler_6 = ClassifyCriticidadeHandler(successor=handler_7)
        handler_5 = ClassifyRiscoHandler(successor=handler_6)
        handler_4 = ZonalHandler(successor=handler_5)
        handler_3 = ValidateRasterHandler(successor=handler_4)
        handler_2 = ValidateVectorHandler(successor=handler_3)
        handler_1 = ValidateOutputHandler(successor=handler_2)

        cqfs = kwargs['cqfs']

        try:
            handler_1.handle(
                line_saida_criticidade=cqfs.dlg.line_saida_criticidade,
                combo_vulnerabilidade=cqfs.dlg.combo_vulnerabilidade,
                combo_risco_fogo=cqfs.dlg.combo_risco_fogo,
                rasters_name=kwargs['rasters_name'],
                objeto=cqfs.criticidade,
                layers=kwargs['layers'],
            )
        except Exception as e:
            cqfs.show_error(str(e))
            self.logger.error(str(e))
