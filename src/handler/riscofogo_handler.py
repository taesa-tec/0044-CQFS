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
from risco_fogo.validate_attribute_handler import ValidateVectorAttributeHandler

from .shared.validate_layer_handler import ValidateVectorHandler
from .shared.validate_output_handler import ValidateOutputHandler
from .shared.validate_layer_handler import ValidateRasterHandler
from CQFS.src.constants import PLUGIN_RISCO_FOGO
from .risco_fogo.rasterize_handler import RasterizeHandler
from .risco_fogo.normalize_handler import NormalizeHandler
from .risco_fogo.riscofogo_model_handler import RiscoFogoModelHandler


class RiscoFogoHandler(Handler):

    def handle(self, **kwargs):

        self.logger.debug('>>> RiscoFogoHandler')
        handler_7 = RiscoFogoModelHandler()
        handler_6 = NormalizeHandler(successor=handler_7)
        handler_5 = RasterizeHandler(successor=handler_6)
        handler_4 = ValidateRasterHandler(successor=handler_5)
        handler_3 = ValidateVectorAttributeHandler(successor=handler_4)
        handler_2 = ValidateVectorHandler(successor=handler_3)
        handler_1 = ValidateOutputHandler(successor=handler_2)
        cqfs = kwargs['cqfs']

        try:
            handler_1.handle(
                line_saida_modelo=cqfs.dlg.line_saida_risco_tecnico,
                combo_vector=cqfs.dlg.combo_risco_fogo_grid_ignicao,
                objeto=cqfs.risco_fogo,
                layers=kwargs['layers'],
                rasters_name=kwargs['rasters_name'],
                plugin_name=PLUGIN_RISCO_FOGO,
                msgselecione='Selecione o Grid',
                msgprojecao='Linha de transmissao nao possui projecao experada "{}".'
            )
        except Exception as e:
            error_msg = u'{} => {}'.format(unicode(e), unicode(traceback.format_exc()))
            self.logger.fatal(error_msg)
            cqfs.show_error(error_msg)
