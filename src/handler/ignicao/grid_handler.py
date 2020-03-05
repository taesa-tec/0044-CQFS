# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-10-04
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
from qgis.core import QgsVectorLayer
from datetime import datetime
from ..handler import Handler
from ....src.spatial_operations import create_grid
from ....src.layer_util import import_layer_qgis


class GridHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 4...')

        original_buffer_layer = kwargs['buffer_layer']

        if original_buffer_layer and original_buffer_layer.isValid():
            buffer_source = unicode(original_buffer_layer.source())

            del original_buffer_layer
            if 'buffer_layer' in kwargs:
                del kwargs['buffer_layer']

            buffer_layer = QgsVectorLayer(buffer_source, 'grid_buffer', 'ogr')

            ext = buffer_layer.extent()
            xmin = float(ext.xMinimum())
            xmax = float(ext.xMaximum())
            ymin = float(ext.yMinimum())
            ymax = float(ext.yMaximum())

            error_msg = None
            if not os.path.isfile(buffer_source):
                error_msg = 'Ignicao buffer does not exist.'

            invalid_extent = 0.0
            if xmin == invalid_extent or xmax == invalid_extent or ymin == invalid_extent or ymax == invalid_extent:
                error_msg = 'Ignicao buffer has invalid extent, got "0.0".'

            if int(buffer_layer.featureCount()) != 1:
                error_msg = 'Ignicao buffer is not valid, has more than one feature.'

            if error_msg is not None:
                self.logger.fatal(error_msg)
                raise RuntimeError(error_msg)

            params = kwargs['cqfs'].ignicao.params
            grid_height = params['grid_height']
            grid_width = params['grid_width']

            start_time = datetime.now()

            line_saida_modelo = kwargs['line_saida_modelo']
            output_source = str(line_saida_modelo.text())

            create_grid(buffer_source, output_source, xmin, xmax, ymin, ymax, grid_height, grid_width)

            end_time = datetime.now()
            time_elapsed = end_time - start_time
            self.logger.info('Summing up, grid time elapsed {}(hh:mm:ss.ms)'.format(time_elapsed))

            if os.path.isfile(output_source):
                kwargs['output_grid_source'] = output_source
                import_layer_qgis(output_source, suffix='', is_vector=True, base_layer=output_source)

                self.next(**kwargs)
            else:
                raise RuntimeError('Fail to create grid "{}".'.format(output_source))
        else:
            raise RuntimeError('Buffer is not valid.')
