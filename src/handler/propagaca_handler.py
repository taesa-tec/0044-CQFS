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
import traceback

from handler import Handler
from .shared.validate_output_handler import ValidateOutputHandler
from .shared.validate_layer_handler import ValidateVectorHandler, ValidateRasterHandler
from .shared.buffer_handler import CreateBufferHandler, ValidateRasterWithBufferHandler
from .propagacao.clip_handler import ClipHandler
from .propagacao.reclassify_handler import ReclassifyHandler
from .propagacao.model_handler import ModelHandler

from ...src.constants import PLUGIN_PROPAGACAO


class PropagacaoHandler(Handler):

    def handle(self, **kwargs):
        handler_8 = ModelHandler()
        handler_7 = ReclassifyHandler(successor=handler_8)
        handler_6 = ClipHandler(successor=handler_7)
        handler_5 = ValidateRasterWithBufferHandler(successor=handler_6)
        handler_4 = CreateBufferHandler(successor=handler_5)
        handler_3 = ValidateRasterHandler(successor=handler_4)
        handler_2 = ValidateVectorHandler(successor=handler_3)
        handler_1 = ValidateOutputHandler(successor=handler_2)

        cqfs = kwargs['cqfs']

        try:
            handler_1.handle(
                line_saida_modelo=cqfs.dlg.line_saida_modelo,
                combo_vector=cqfs.dlg.combo_linha_transmissao,
                objeto=cqfs.propagacao,
                layers=kwargs['layers'],
                rasters_name=kwargs['rasters_name'],
                plugin_name=PLUGIN_PROPAGACAO,
                proj4=cqfs.propagacao.proj4,
                open_output_layer=True
            )
        except Exception as e:
            error_msg = u'{} => {}'.format(unicode(e), unicode(traceback.format_exc()))
            self.logger.fatal(error_msg)
            cqfs.show_error(error_msg)
