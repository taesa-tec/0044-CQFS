# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-09-10
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
import logging

from PyQt4.QtCore import QVariant
from constants import PLUGIN_CRITICIDADE
from cqfs_config import load_config
from qgis.core import QgsField, QgsVectorLayer, QgsMapLayerRegistry
from qt_handler import QtHandler
from layer_util import find_one_layer_by_name
from ..src.fillcell.zonal_statistics_new_layer import ZonalStatisticsNewLayer

__logger = logging.getLogger(PLUGIN_CRITICIDADE)


class Criticidade(object):
    logger = logging.getLogger(PLUGIN_CRITICIDADE)
    cqfs_config = load_config()
    params = cqfs_config[PLUGIN_CRITICIDADE]
    proj4 = cqfs_config['global']['crs_proj4']

    def __init__(self, rasters_name, vectors_name, combo_vulnerabilidade, combo_risco_fogo):

        self.logger.error('Init criticidade')

        self.__qt = QtHandler()
        self.__qt.init_combobox(
            rasters_name,
            risco_fogo=combo_risco_fogo
        )

        QtHandler.set_combobox(combo_vulnerabilidade, vectors_name, self.on_vulnerabilidade_change)
        QtHandler.set_combobox(combo_risco_fogo, rasters_name, self.on_risco_fogo_change)

        self.__combo_vulnerabilidade = combo_vulnerabilidade
        self.__combo_risco_fogo = combo_risco_fogo

    def validate_vulnerabilidade(self, layers, combo_vulnerabilidade):
        vulnerabilidade_index = combo_vulnerabilidade.currentIndex()

        if combo_vulnerabilidade <= 0:
            return 'Selecione o shape de Vulnerabilidade.', None

        # validação de atributos

        layer_vulnerabilidade = self.validate_attributes(layers, combo_vulnerabilidade, vulnerabilidade_index,
                                                         'attributes_vulnerabilidade')

        return None, layer_vulnerabilidade

    def validate_attributes(self, layers, combo, index, attributes_name):
        name = combo.itemText(index)
        layer = find_one_layer_by_name(layers, name)

        attributes = self.params[attributes_name]
        fields = [str(field.name()) for field in layer.pendingFields()]

        for attr in attributes:
            if str(attr) not in fields:
                self.logger.error('Layer Attributes "{}" error on validation attributes...'.format(str(attr)))
                return 'Erro na validacao de atributos.', None
        return layer

    def destroy(self):
        self.__combo_vulnerabilidade.clear()
        self.__combo_risco_fogo.clear()

        self.__qt.clear_combobox()

        self.__qt = None
        self.__combo_vulnerabilidade = None
        self.__combo_risco_fogo = None

    @property
    def combo_name_by_layer_index(self):
        return self.__qt.combo_name_by_layer_index

    def generate_zonal(self, vao, risco_fogo, output):
        zs = ZonalStatisticsNewLayer(vao.source(), risco_fogo.source(), output, operations=('max',), fields_alias=('CRIT',))
        zs.perform()

        output_layer = QgsVectorLayer(output, 'risco_zs', 'ogr')
        QgsMapLayerRegistry.instance().addMapLayers([output_layer])

        return None, output_layer

    def classify_risco(self, layer):

        _, bar = QtHandler.progress_dialog(label='Classifying Risk...')

        fields = [str(field.name()) for field in layer.pendingFields()]

        pr = layer.dataProvider()

        bar.setValue(20)

        if self.params['att_cls_criticidade'] not in fields:
            pr.addAttributes([QgsField(self.params['att_cls_criticidade'], QVariant.String)])

        layer.updateFields()
        bar.setValue(50)

        layer.startEditing()
        for feature in layer.getFeatures():
            criticidade = feature[self.params['att_criticidade']]
            classificacao = self.classify(criticidade)
            layer.changeAttributeValue(feature.id(), layer.fieldNameIndex(self.params['att_cls_criticidade']), classificacao)

        layer.commitChanges()

        bar.setValue(100)
        return None, layer

    def classify(self, criticidade):
        if criticidade <= 0.2:
            return self.params['classif_muito_baixa']

        elif 0.2 < criticidade < 0.4:
            return self.params['classif_baixa']

        elif 0.4 < criticidade < 0.6:
            return self.params['classif_media']

        elif 0.6 < criticidade < 0.8:
            return self.params['classif_alta']

        elif criticidade >= 0.8:
            return self.params['classif_muito_alta']

    @staticmethod
    def on_vulnerabilidade_change(combo, index):
        if index == 0:
            return

    def on_risco_fogo_change(self, combo, index):
        self.__qt.on_combobox_change('risco_fogo', combo, index)

