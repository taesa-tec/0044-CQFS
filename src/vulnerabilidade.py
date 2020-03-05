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
from constants import PLUGIN_PROPAGACAO, PLUGIN_VULNERABILIDADE, PLUGIN_VULNERABILIDADE_VAO, PLUGIN_VULNERABILIDADE_PC, \
    PLUGIN_VULNERABILIDADE_TORRE
from qgis._core import QgsField
from qt_handler import QtHandler
from cqfs_config import load_config
from layer_util import find_one_layer_by_name
from ..src.plugin_util import validate_vectors

__logger = logging.getLogger(PLUGIN_VULNERABILIDADE)


class Vulnerabilidade(object):
    logger = logging.getLogger(PLUGIN_VULNERABILIDADE)
    cqfs_config = load_config()
    params = cqfs_config[PLUGIN_VULNERABILIDADE]
    proj4 = cqfs_config['global']['crs_proj4']

    def __init__(self, vectors_vao_name, vectors_name, combo_vao, combo_ponto_critico, combo_torre):

        self.logger.error('Init vulnerabilidade')

        self.__qt = QtHandler()

        self.__combo_vao = combo_vao
        self.__combo_ponto_critico = combo_ponto_critico
        self.__combo_torre = combo_torre

        self.__init_combobox(vectors_name)

        QtHandler.set_combobox(combo_vao, vectors_vao_name, self.on_vao_change)
        QtHandler.set_combobox(combo_ponto_critico, vectors_name, self.on_ponto_critico_change)
        QtHandler.set_combobox(combo_torre, vectors_name, self.on_torre_change)

    def destroy(self):
        self.__combo_vao.clear()
        self.__combo_ponto_critico.clear()
        self.__combo_torre.clear()

        self.__qt.clear_combobox()

        self.__qt = None
        self.__combo_vao = None
        self.__combo_ponto_critico = None
        self.__combo_torre = None

    def validate(self, layers, combo_vao, combo_ponto_critico, combo_torres):
        vao_index = combo_vao.currentIndex()
        ponto_critico_index = combo_ponto_critico.currentIndex()
        torres_index = combo_torres.currentIndex()

        if vao_index <= 0:
            return 'Selecione o vão.', None

        if ponto_critico_index <= 0:
            return 'Selecione o ponto critico.', None

        if torres_index <= 0:
            return 'Selecione as torres.', None

        # validação de atributos

        layer_vao = self.validate_attributes(layers, combo_vao, vao_index, 'attributes_vao')
        layer_pc = self.validate_attributes(layers, combo_ponto_critico, ponto_critico_index, 'attributes_ponto_critico')
        layer_torres = self.validate_attributes(layers, combo_torres, torres_index, 'attributes_torres')

        self.verify_group_attribute(layer_vao)
        self.verify_group_attribute(layer_torres)

        validate_vectors(layers, combo_vao, self.proj4)
        validate_vectors(layers, combo_ponto_critico, self.proj4)
        validate_vectors(layers, combo_torres, self.proj4)

        prov = layer_vao.dataProvider()
        attr_type = prov.fields().field(self.params['att_vao_id']).type()

        if attr_type not in (QVariant.Int, QVariant.Double):
            return 'A coluna "{}" deve ser numerica.'.format(self.params['att_vao_id']), None, None, None

        return None, layer_vao, layer_pc, layer_torres

    def validate_attributes(self, layers, combo, index, attributes_name):
        name = combo.itemText(index)
        layer = find_one_layer_by_name(layers, name)

        attributes = load_config()['vulnerabilidade'][attributes_name]
        fields = [str(field.name()) for field in layer.pendingFields()]

        for attr in attributes:
            if str(attr) not in fields:
                self.logger.error('Layer Attributes "{}" error on validation attributes...'.format(str(attr)))
                return 'Erro na validacao do atributo "{}".'.format(str(attr)), None
                break
        return layer

    def verify_group_attribute(self, layer):
        fields = [str(field.name()) for field in layer.pendingFields()]
        grupo = self.params['att_grupo']

        if grupo not in fields:
            pr = layer.dataProvider()
            pr.addAttributes([QgsField(self.params['att_grupo'], QVariant.Int)])
            layer.updateFields()

        return

    def __init_combobox(self, vectors_name):
        combo = {
            PLUGIN_VULNERABILIDADE_PC: self.__combo_ponto_critico,
            PLUGIN_VULNERABILIDADE_TORRE: self.__combo_torre,
        }

        self.__qt.init_combobox(vectors_name, **combo)

    def on_vao_change(self, combo, index):
        if index == 0:
            return

    def on_ponto_critico_change(self, combo, index):
        self.__qt.on_combobox_change(PLUGIN_VULNERABILIDADE_PC, combo, index)

    def on_torre_change(self, combo, index):
        self.__qt.on_combobox_change(PLUGIN_VULNERABILIDADE_TORRE, combo, index)

