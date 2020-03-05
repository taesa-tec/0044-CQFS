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
from ..handler import Handler
from ....src.fillcell.zonal_statistics import ZonalStatistics


class FillRasterHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 1...')

        cqfs = kwargs['cqfs']
        ignicao = cqfs.ignicao
        params = ignicao.params['fill_cell']['raster']

        grid = kwargs['vector_layer']
        grid_source = grid.source()

        raster_by_combo_name = kwargs['raster_by_combo_name']

        errors = []
        success = True

        try:
            for name, raster in raster_by_combo_name.iteritems():
                raster_params = params[name]
                raster_source = raster.source()

                fields_alias = tuple(raster_params['fields'])
                operations = tuple(raster_params['operations'])

                zs = ZonalStatistics(grid_source, raster_source, fields_alias=fields_alias, operations=operations)
                zs.perform()
        except Exception as e:
            self.logger.error(str(e))
            errors.append(str(e))
            success = False
            cqfs.show_error(str(e))

        del kwargs['vector_layer']

        if success:
            kwargs['grid_source'] = grid_source
            self.next(**kwargs)
        else:
            self.error = ', '.join(errors)
            self.logger.fatal(self.error)
            raise RuntimeError(self.error)
