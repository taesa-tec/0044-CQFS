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
from layer_util import find_one_layer_by_name
from layer_util import has_correct_crs
from qt_handler import QtHandler
from layer_util import is_raster_valid as raster_ok


def validate_vectors(layers, combo, proj4,
                     msgselecione=u'Selecione a linha de transmissao.',
                     msgprojecao=u'Linha de transmissao nao possui projecao experada "{}".'):
    msgselecione = unicode(msgselecione)
    msgprojecao = unicode(msgprojecao)
    proj4 = unicode(proj4)

    layer = layer_from_combo(layers, combo)

    if not layer:
        return msgselecione, None

    if not has_correct_crs(layer, proj4):
        return msgprojecao.format(proj4), None
    return None, layer


def layer_from_combo(layers, combo):
    idx = combo.currentIndex()

    if idx <= 0:
        return None

    name = combo.itemText(idx)
    return find_one_layer_by_name(layers, name)


def validate_rasters(objeto, layers, rasters, proj4):

    combo_by_index = objeto.combo_name_by_layer_index
    for combo_name, idx in combo_by_index.iteritems():
        if idx <= 0:
            return u'Selecione um raster para o combo box "{}".'.format(combo_name), None

    current = 0
    size = len(combo_by_index)
    _, bar = QtHandler.progress_dialog(label='Validating rasters...')

    rasters_selected = []
    for combo_name, idx in combo_by_index.iteritems():
        raster_name = rasters[idx]
        layer = find_one_layer_by_name(layers, raster_name)
        config = objeto.params['raster'][combo_name]
        if not raster_ok(config, layer, proj4):
            return u'Raster "{}" selecionado no combo box "{}" e invalido!'.format(layer.name(), combo_name), None

        rasters_selected.append(layer)

        current += 1
        progress = (float(current) / float(size)) * 100
        bar.setValue(progress)
    return None, rasters_selected
