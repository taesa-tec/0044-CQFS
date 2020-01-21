# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-10-01
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
import traceback

from ..handler import Handler
from ....src.handler.shared.validate_output_handler import ValidateOutputHandler
from ....src.handler.shared.validate_layer_handler import ValidateVectorHandler
from ....src.handler.shared.buffer_handler import CreateBufferHandler
from ....src.cqfs_config import tmp_filename_without_extension, strtimestamp
from ....src.plugin_util import layer_from_combo
from grid_handler import GridHandler


class CreateHandler(Handler):

    def handle(self, **kwargs):
        cqfs = kwargs['cqfs']

        linha_transmissao = layer_from_combo(kwargs['layers'], cqfs.dlg.ignicao_combo_lt)

        buffer_source = ''
        if linha_transmissao and linha_transmissao.isValid():
            uni_source = linha_transmissao.source()
            buffer_source = unicode(uni_source)

            buffer_source = unicode(os.path.dirname(os.path.abspath(buffer_source)))
            buffer_source = os.path.join(buffer_source, unicode('_tmp_buffer_' + strtimestamp() + '.shp'))

        if buffer_source == '':
            buffer_source = unicode(tmp_filename_without_extension() + '.shp')

        kwargs['buffer_source'] = buffer_source
        kwargs['open_output_layer'] = True

        handler_4 = GridHandler(successor=None)
        handler_3 = CreateBufferHandler(successor=handler_4)
        handler_2 = ValidateVectorHandler(successor=handler_3)
        handler_1 = ValidateOutputHandler(successor=handler_2)

        try:
            handler_1.handle(**kwargs)
        except Exception as e:
            error_msg = u'{} => {}'.format(unicode(e), unicode(traceback.format_exc()))
            self.logger.fatal(error_msg)
            cqfs.show_error(error_msg)
