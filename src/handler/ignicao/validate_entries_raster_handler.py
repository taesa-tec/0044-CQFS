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
from ...handler.handler import Handler
from ....src.cqfs_config import load_config
from ....src.qt_handler import QtHandler
from ....src.layer_util import find_one_layer_by_name, is_raster_valid as raster_ok

cqfs_config = load_config()
proj4 = cqfs_config['global']['crs_proj4']


class ValidateEntriesRasterHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 3...')

        cqfs = kwargs['cqfs']
        layers = kwargs['layers']
        rasters_name = kwargs['rasters_name']
        
        ignicao = cqfs.ignicao
        params = ignicao.params
        fill_cell = params['fill_cell']['raster']
        combo_by_index = ignicao.combo_name_by_raster_index

        current = 0
        size = len(combo_by_index)
        dlg, bar = QtHandler.progress_dialog(label='Validating rasters...')
    
        fill = {}
        last_progress = 0
        for combo_name, idx in combo_by_index.iteritems():
            if combo_name in fill_cell and idx > 0:
                name = rasters_name[idx]
                layer = find_one_layer_by_name(layers, name)
                config = params['raster'][combo_name]
                if not raster_ok(config, layer, proj4):
                    raise RuntimeError(u'Raster "{}" selecionado no combo box "{}" e invalido!'.format(layer.name(), combo_name))

                fill[combo_name] = layer

            current += 1
            progress = (float(current) / float(size)) * 100
            bar.setValue(progress)
            last_progress = progress

        if last_progress < 100:
            bar.setValue(100)

        bar.close()
        dlg.close()
        del dlg

        kwargs['raster_by_combo_name'] = fill
        self.next(**kwargs)
