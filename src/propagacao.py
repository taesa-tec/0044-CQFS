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
from re import findall

from constants import PLUGIN_PROPAGACAO
from constants import PLUGIN_PROPAGACAO_HIPSOMETRIA
from constants import PLUGIN_PROPAGACAO_CLINOGRAFIA
from constants import PLUGIN_PROPAGACAO_ORIENTACAO_VERTENTE
from constants import PLUGIN_PROPAGACAO_PROXIMIDADE_ESTRADAS
from constants import PLUGIN_PROPAGACAO_VEGETACAO

from cqfs_config import load_config, tmp_filename_without_extension
from layer_util import find_one_layer_by_name
from layer_util import import_layer_qgis
from layer_util import is_raster_valid as raster_ok
from layer_util import raster_calculator_from_config
from layer_util import set_layer_style
from qt_handler import QtHandler
from reclass.propagacao_clinografia_reclass import PropagacaoClinografiaReclass
from reclass.propagacao_hipsometria_reclass import PropagacaoHipsometriaReclass
from reclass.propagacao_model_reclass import PropagacaoModelReclass
from reclass.propagacao_orientacao_vertente_reclass import PropagacaoOrientacaoVertenteReclass
from reclass.propagacao_proximidade_estradas_reclass import PropagacaoProximidadeEstradasReclass
from reclass.propagacao_vegetacao_reclass import PropagacaoVegetacaoReclass
from reclassify import Reclassify

config = load_config()


class Propagacao(object):
    logger = logging.getLogger(PLUGIN_PROPAGACAO)
    params = config[PLUGIN_PROPAGACAO]
    proj4 = config['global']['crs_proj4']

    reclass_algorithms = {
        PLUGIN_PROPAGACAO_HIPSOMETRIA: PropagacaoHipsometriaReclass,
        PLUGIN_PROPAGACAO_CLINOGRAFIA: PropagacaoClinografiaReclass,
        PLUGIN_PROPAGACAO_ORIENTACAO_VERTENTE: PropagacaoOrientacaoVertenteReclass,
        PLUGIN_PROPAGACAO_PROXIMIDADE_ESTRADAS: PropagacaoProximidadeEstradasReclass,
        PLUGIN_PROPAGACAO_VEGETACAO: PropagacaoVegetacaoReclass
    }

    def __init__(self, vectors_name, rasters_name, combo_linha_transmissao, combo_vegetacao, combo_clinografia,
                 combo_orientacao_vertente, combo_proximidade_estradas, combo_hipsometria):
        self.__qt = QtHandler()
        self.__qt.init_combobox(
            rasters_name,
            vegetacao=combo_vegetacao,
            clinografia=combo_clinografia,
            orientacao_vertente=combo_orientacao_vertente,
            proximidade_estradas=combo_proximidade_estradas,
            hipsometria=combo_hipsometria
        )

        QtHandler.set_combobox(combo_vegetacao, rasters_name, self.on_vegetacao_change)
        QtHandler.set_combobox(combo_clinografia, rasters_name, self.on_clinografia_change)
        QtHandler.set_combobox(combo_orientacao_vertente, rasters_name, self.on_orientacao_vertente_change)
        QtHandler.set_combobox(combo_proximidade_estradas, rasters_name, self.on_proximidade_estradas_change)
        QtHandler.set_combobox(combo_hipsometria, rasters_name, self.on_hipsometria_change)
        QtHandler.set_combobox(combo_linha_transmissao, vectors_name, self.on_linha_transmissao_change)

        self.__combo_vegetacao = combo_vegetacao
        self.__combo_clinografia = combo_clinografia
        self.__combo_orientacao_vertente = combo_orientacao_vertente
        self.__combo_proximidade_estradas = combo_proximidade_estradas
        self.__combo_hipsometria = combo_hipsometria
        self.__combo_linha_transmissao = combo_linha_transmissao

    def destroy(self):
        self.__combo_vegetacao.clear()
        self.__combo_clinografia.clear()
        self.__combo_orientacao_vertente.clear()
        self.__combo_proximidade_estradas.clear()
        self.__combo_hipsometria.clear()
        self.__combo_linha_transmissao.clear()

        self.__qt.clear_combobox()

        self.__qt = None
        self.__combo_vegetacao = None
        self.__combo_clinografia = None
        self.__combo_orientacao_vertente = None
        self.__combo_proximidade_estradas = None
        self.__combo_hipsometria = None
        self.__combo_linha_transmissao = None

    @property
    def combo_name_by_layer_index(self):
        return self.__qt.combo_name_by_layer_index

    def reclassify(self, layers, rasters):
        suffix = '_clipped'
        sources = {}
        layers_by_name = {}

        combo_by_index = self.__qt.combo_name_by_layer_index

        current = 0
        size = len(combo_by_index)
        total = 100 / size
        last_progress = 0
        dlg, bar = QtHandler.progress_dialog(label='Reclassifying rasters...')

        for combo_name, idx in combo_by_index.iteritems():
            raster_name = rasters[idx]
            raster_name = raster_name + suffix
            self.logger.info('Searching raster to reclassify, index {} ({})...'.format(idx, raster_name))
            layer = find_one_layer_by_name(layers, raster_name)

            if not layer:
                self.logger.warn('Layer "{}" not found to reclassify...'.format(raster_name))
                return

            input_raster = layer.source()
            output_raster = tmp_filename_without_extension() + '.tif'

            algorithm = self.reclass_algorithms[combo_name]
            reclass = algorithm(input_raster, output_raster)
            re = Reclassify(reclass)
            re.apply()

            sources[combo_name] = output_raster

            current += 1
            percentage = int(current * total)
            self.logger.info('Reclassify status: {}%...'.format(str(percentage)))
            bar.setValue(percentage)
            last_progress = percentage

        if last_progress < 100:
            bar.setValue(100)

        bar.close()
        dlg.close()
        del dlg

        for combo_name, source in sources.iteritems():
            output = import_layer_qgis(source, suffix='reclass', base_layer=combo_name, add_map_layer=False)
            layers_by_name[combo_name] = output
        return layers_by_name

    def apply_model(self, vegetacao, clinografia, orientacao_vertente, proximidade_estradas, hipsometria,
                    output_raster):
        """
        Apply propagacao model.

        :param vegetacao: A QgsRasterLayer layer.
        :param clinografia: A QgsRasterLayer layer.
        :param orientacao_vertente: A QgsRasterLayer layer.
        :param proximidade_estradas: A QgsRasterLayer layer.
        :param hipsometria: A QgsRasterLayer layer.
        :param output_raster: A string with the layer output path.
        :return: QgsRasterLayer
        """
        dlg, bar = QtHandler.progress_dialog(label='Applying model...')

        expression_template = self.params['expression']
        default_band = self.params['expression_default_band']
        expression_base_layer = self.params['expression_base_layer']

        qgs_raster_layers = [vegetacao, clinografia, orientacao_vertente, proximidade_estradas, hipsometria]
        expression_alias = findall(r'\{(.*?)\}', expression_template)

        bar.setValue(10)

        idx = expression_alias.index(expression_base_layer)
        qgs_raster_base_layer = qgs_raster_layers[idx]
        tmp_output_raster = tmp_filename_without_extension() + '.tif'

        bar.setValue(20)

        code, msg = raster_calculator_from_config(qgs_raster_layers, expression_alias, expression_template, qgs_raster_base_layer, tmp_output_raster, default_band)

        bar.setValue(80)

        if code == 0:
            propagacao = PropagacaoModelReclass(tmp_output_raster, output_raster)
            re = Reclassify(propagacao)
            re.apply()

            layer = import_layer_qgis(output_raster)
            set_layer_style(layer, PLUGIN_PROPAGACAO, PLUGIN_PROPAGACAO)
        else:
            self.logger.fatal(msg)

        bar.setValue(100)

        bar.close()
        dlg.close()
        del dlg

        return code, msg

    def on_vegetacao_change(self, combo, index):
        self.__qt.on_combobox_change(PLUGIN_PROPAGACAO_VEGETACAO, combo, index)

    def on_clinografia_change(self, combo, index):
        self.__qt.on_combobox_change(PLUGIN_PROPAGACAO_CLINOGRAFIA, combo, index)

    def on_orientacao_vertente_change(self, combo, index):
        self.__qt.on_combobox_change(PLUGIN_PROPAGACAO_ORIENTACAO_VERTENTE, combo, index)

    def on_proximidade_estradas_change(self, combo, index):
        self.__qt.on_combobox_change(PLUGIN_PROPAGACAO_PROXIMIDADE_ESTRADAS, combo, index)

    def on_hipsometria_change(self, combo, index):
        self.__qt.on_combobox_change(PLUGIN_PROPAGACAO_HIPSOMETRIA, combo, index)

    @staticmethod
    def on_linha_transmissao_change(combo, index):
        if index == 0:
            return
