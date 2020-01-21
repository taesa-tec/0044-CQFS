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
import os
import traceback

from ..handler import Handler
from fill_raster_handler import FillRasterHandler
from fill_vector_handler import FillVectorHandler
from validate_entries_raster_handler  import ValidateEntriesRasterHandler
from validate_entries_vector_handler import ValidateEntriesVectorHandler
from ....src.handler.shared.validate_layer_handler import ValidateVectorHandler


class FillHandler(Handler):

    def handle(self, **kwargs):
        cqfs = kwargs['cqfs']

        handler_5 = FillVectorHandler(successor=None)
        handler_4 = FillRasterHandler(successor=handler_5)
        handler_3 = ValidateEntriesVectorHandler(successor=handler_4)
        handler_2 = ValidateEntriesRasterHandler(successor=handler_3)
        handler_1 = ValidateVectorHandler(successor=handler_2)

        try:
            handler_1.handle(**kwargs)
        except Exception as e:
            error_msg = u'{} => {}'.format(unicode(e), unicode(traceback.format_exc()))
            self.logger.fatal(error_msg)
            cqfs.show_error(error_msg)
