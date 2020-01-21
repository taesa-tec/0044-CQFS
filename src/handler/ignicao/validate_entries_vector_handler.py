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
from ....src.constants import PLUGIN_IGNICAO_QUEIMADAS
from ....src.cqfs_config import load_config
from ....src.qt_handler import QtHandler
from ....src.layer_util import find_one_layer_by_name, has_correct_crs, validate_fields

cqfs_config = load_config()
proj4 = cqfs_config['global']['crs_proj4']


class ValidateEntriesVectorHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 4...')

        cqfs = kwargs['cqfs']
        layers = kwargs['layers']
        polygons_name = kwargs['polygons_name']
        
        ignicao = cqfs.ignicao
        params = ignicao.params['fill_cell']['vector']
        combo_by_index = ignicao.combo_name_by_vector_index

        current = 0
        size = len(combo_by_index)
        dlg, bar = QtHandler.progress_dialog(label='Validating vectors...')

        msgprojecao = 'Dado de entrada "{}" nao possui projecao experada "{}".'
    
        fill = {}
        last_progress = 0
        for combo_name, idx in combo_by_index.iteritems():
            if combo_name in params and idx > 0:
                name = polygons_name[idx]
                layer = find_one_layer_by_name(layers, name)

                if not has_correct_crs(layer, proj4):
                    raise RuntimeError(msgprojecao.format(name, proj4))

                layer_property = params[combo_name]
                if isinstance(layer_property, dict):
                    self.has_fields_present(layer, layer_property)

                fill[combo_name] = layer

            current += 1
            progress = (float(current) / float(size)) * 100
            bar.setValue(progress)
            last_progress = progress

        queimadas = ignicao.combo_queimadas_layer_name
        if queimadas:
            layer = find_one_layer_by_name(layers, queimadas)
            if not has_correct_crs(layer, proj4):
                raise RuntimeError(msgprojecao.format(queimadas, proj4))
            fill[PLUGIN_IGNICAO_QUEIMADAS] = layer

        if last_progress < 100:
            bar.setValue(100)

        bar.close()
        dlg.close()
        del dlg

        kwargs['vector_by_combo_name'] = fill
        self.next(**kwargs)

    @staticmethod
    def has_fields_present(layer, layer_property):
        attributes = []
        for _, prop in layer_property.iteritems():
            attributes.append(str(prop['alias']).lower())

        missing_fields = validate_fields(layer, attributes)
        if len(missing_fields) > 0:
            raise RuntimeError(u', '.join(missing_fields))
