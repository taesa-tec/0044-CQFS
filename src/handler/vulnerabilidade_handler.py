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
from vulnerabilidade.save_file_handler import RemoveLayersHandler
from vulnerabilidade.clip_handler import ClipHandler
from vulnerabilidade.calculate_handler import CalculateHandler
from vulnerabilidade.buffer_handler import CreateBufferPCHandler, BufferClipHandler
from vulnerabilidade.line_handler import CreateLineHandler, CreateLinePCHandler
from vulnerabilidade.validate_layer_handler import ValidateVectorHandler
from vulnerabilidade.validate_output_handler import ValidateOutputHandler


class VulnerabilidadeHandler(Handler):

    def handle(self, **kwargs):

        self.logger.error('>>> VulnerabilidadeHandler')
        handler_9 = RemoveLayersHandler(successor=None)
        handler_8 = BufferClipHandler(successor=handler_9)
        handler_7 = ClipHandler(successor=handler_8)
        handler_6 = CreateLinePCHandler(successor=handler_7)
        handler_5 = CreateBufferPCHandler(successor=handler_6)
        handler_4 = CalculateHandler(successor=handler_5)
        handler_3 = CreateLineHandler(successor=handler_4)
        handler_2 = ValidateVectorHandler(successor=handler_3)
        handler_1 = ValidateOutputHandler(successor=handler_2)

        cqfs = kwargs['cqfs']

        try:
            handler_1.handle(
                line_saida_vulnerabilidade=cqfs.dlg.line_saida_vulnerabilidade,
                combo_vao=cqfs.dlg.combo_vao,
                combo_ponto_critico=cqfs.dlg.combo_ponto_critico,
                combo_torres=cqfs.dlg.combo_torres,
                vulnerabilidade=cqfs.vulnerabilidade,
                layers=kwargs['layers'],
            )
        except Exception as e:
            cqfs.show_error(str(e))
