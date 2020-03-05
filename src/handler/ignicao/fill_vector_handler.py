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
import traceback

from ..handler import Handler
from ....src.fillcell.cellular_space import CellularSpace
from ....src.fillcell.presence import Presence
from ....src.constants import PLUGIN_IGNICAO_QUEIMADAS

class FillVectorHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 2...')

        cqfs = kwargs['cqfs']
        grid_source = kwargs['grid_source']
        vector_by_combo_name = kwargs['vector_by_combo_name']

        ignicao = cqfs.ignicao
        params = ignicao.params['fill_cell']['vector']

        success = True
        has_queimadas = False

        try:
            for name, vector in vector_by_combo_name.iteritems():
                if name == unicode(PLUGIN_IGNICAO_QUEIMADAS):
                    has_queimadas = True
                    continue

                vector_params = params[name]
                vector_source = vector.source()

                field_to_check_null = None
                for field_name, props in vector_params.iteritems():
                    if 'field_to_check_null' in props:
                        field_to_check_null = field_name
                        break

                if field_to_check_null is None:
                    raise RuntimeError('Fail to find property "field_to_check_null" in cqfs.yaml of "{}"'.format(name))

                cs = CellularSpace(
                    grid_source,
                    vector_source,
                    field_to_check_null,
                    vector_params
                )

                cs.fill_cell()

            if has_queimadas:
                field_name = params[PLUGIN_IGNICAO_QUEIMADAS]
                vector = vector_by_combo_name[PLUGIN_IGNICAO_QUEIMADAS]
                vector_source = vector.source()

                ps = Presence(
                    grid_source,
                    vector_source,
                    field_name
                )

                ps.fill_cell()
        except Exception as e:
            success = False
            self.error = u'{} => {}'.format(unicode(e), unicode(traceback.format_exc()))
            self.logger.error(u'Fail to run fill vector: {}'.format(unicode(self.error)))
            cqfs.show_error(unicode(e))

        if success:
            self.next(**kwargs)
