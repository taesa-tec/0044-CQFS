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

from math import exp
from datetime import datetime
from qgis.core import QgsField, NULL
from PyQt4.QtCore import QVariant

from constants import PLUGIN_IGNICAO
from constants import PLUGIN_IGNICAO_INSOLACAO
from constants import PLUGIN_IGNICAO_TEMPERATURA_MAXIMA
from constants import PLUGIN_IGNICAO_VELOCIDADE_VENTO
from constants import PLUGIN_IGNICAO_CENSO_IBGE
from constants import PLUGIN_IGNICAO_USO_SOLO
from constants import PLUGIN_IGNICAO_GNDVI
from constants import PLUGIN_IGNICAO_NDVI
from constants import PLUGIN_IGNICAO_AREA_BASAL
from constants import PLUGIN_IGNICAO_DENSIDADE
from constants import PLUGIN_IGNICAO_VOLUME
from constants import PLUGIN_IGNICAO_ALTITUDE
from constants import PLUGIN_IGNICAO_GRID

from cqfs_config import load_config
from qt_handler import QtHandler

config = load_config()


class Ignicao(object):
    logger = logging.getLogger(PLUGIN_IGNICAO)
    pt_br_format = '%d/%m/%Y %H:%M'

    params = config[PLUGIN_IGNICAO]
    proj4 = config['global']['crs_proj4']

    def __init__(self, dlg, rasters_name, lines_name, polygons_name, points_name):
        # input vectors
        self.__ignicao_group_entrada_modelo = dlg.ignicao_group_entrada_modelo
        self.__ignicao_checkbox_lt = dlg.ignicao_checkbox_lt
        self.__ignicao_combo_lt = dlg.ignicao_combo_lt

        self.__ignicao_group_grid = dlg.ignicao_group_grid
        self.__ignicao_checkbox_grid = dlg.ignicao_checkbox_grid
        self.__ignicao_combo_grid = dlg.ignicao_combo_grid

        # input rasters
        self.__ignicao_group_entradas_modelo = dlg.ignicao_group_entradas_modelo
        self.__ignicao_checkbox_habilitar_entradas = dlg.ignicao_checkbox_habilitar_entradas

        self.__ignicao_combo_insolacao = dlg.ignicao_combo_insolacao
        self.__ignicao_combo_temperatura_maxima = dlg.ignicao_combo_temperatura_maxima
        self.__ignicao_combo_velocidade_vento = dlg.ignicao_combo_velocidade_vento
        self.__ignicao_combo_censo_ibge = dlg.ignicao_combo_censo_ibge
        self.__ignicao_combo_uso_solo = dlg.ignicao_combo_uso_solo
        self.__ignicao_combo_gndvi = dlg.ignicao_combo_gndvi
        self.__ignicao_combo_ndvi = dlg.ignicao_combo_ndvi
        self.__ignicao_combo_area_basal = dlg.ignicao_combo_area_basal
        self.__ignicao_combo_densidade = dlg.ignicao_combo_densidade
        self.__ignicao_combo_volume = dlg.ignicao_combo_volume
        self.__ignicao_combo_queimadas = dlg.ignicao_combo_queimadas
        self.__ignicao_combo_altitude = dlg.ignicao_combo_altitude

        # formula
        self.__ignicao_group_formula_saida = dlg.ignicao_group_formula_saida
        self.__ignicao_checkbox_habilitar_formula = dlg.ignicao_checkbox_habilitar_formula
        self.__ignicao_btn_entrada_formula = dlg.ignicao_btn_entrada_formula
        self.__ignicao_line_entrada_formula = dlg.ignicao_line_entrada_formula

        # output grid
        self.__ignicao_group_grid_saida = dlg.ignicao_group_grid_saida
        self.__ignicao_btn_saida_modelo = dlg.ignicao_btn_saida_modelo
        self.__ignicao_line_saida_modelo = dlg.ignicao_line_saida_modelo

        self.__create_fill_grid = False
        self.__fill_grid = False
        self.__apply_formula = False

        self.__qt_raster = QtHandler()
        self.__qt_vector = QtHandler()

        self.__init_combobox(rasters_name, polygons_name)
        self.__init_qt(rasters_name, lines_name, polygons_name, points_name)

        self.logger.info('Ignicao instance create successfully.')

    def destroy(self):
        self.__ignicao_combo_lt.clear()
        self.__ignicao_combo_queimadas.clear()

        self.__ignicao_combo_grid.clear()

        self.__ignicao_combo_insolacao.clear()
        self.__ignicao_combo_temperatura_maxima.clear()
        self.__ignicao_combo_velocidade_vento.clear()
        self.__ignicao_combo_censo_ibge.clear()
        self.__ignicao_combo_uso_solo.clear()
        self.__ignicao_combo_gndvi.clear()
        self.__ignicao_combo_ndvi.clear()
        self.__ignicao_combo_area_basal.clear()
        self.__ignicao_combo_densidade.clear()
        self.__ignicao_combo_volume.clear()
        self.__ignicao_combo_altitude.clear()

        self.__qt_raster.clear_combobox()
        self.__qt_vector.clear_combobox()

        QtHandler.disconnect(self.__ignicao_combo_lt.currentIndexChanged)
        QtHandler.disconnect(self.__ignicao_combo_queimadas.currentIndexChanged)

        QtHandler.disconnect(self.__ignicao_checkbox_lt.toggled)
        QtHandler.disconnect(self.__ignicao_checkbox_grid.toggled)
        QtHandler.disconnect(self.__ignicao_checkbox_habilitar_entradas.toggled)
        QtHandler.disconnect(self.__ignicao_checkbox_habilitar_formula.toggled)

        self.__qt_raster = None
        self.__qt_vector = None

        self.__ignicao_combo_lt = None
        self.__ignicao_combo_grid = None

        self.__ignicao_combo_insolacao = None
        self.__ignicao_combo_temperatura_maxima = None
        self.__ignicao_combo_velocidade_vento = None
        self.__ignicao_combo_censo_ibge = None
        self.__ignicao_combo_uso_solo = None
        self.__ignicao_combo_gndvi = None
        self.__ignicao_combo_ndvi = None
        self.__ignicao_combo_area_basal = None
        self.__ignicao_combo_densidade = None
        self.__ignicao_combo_volume = None
        self.__ignicao_combo_queimadas = None
        self.__ignicao_combo_altitude = None

    @property
    def is_create(self):
        return self.__create_fill_grid

    @property
    def is_fill(self):
        return self.__create_fill_grid or self.__fill_grid

    @property
    def is_formula(self):
        return self.__apply_formula

    @property
    def combo_name_by_raster_index(self):
        return self.__qt_raster.combo_name_by_layer_index

    @property
    def combo_name_by_vector_index(self):
        return self.__qt_vector.combo_name_by_layer_index

    @property
    def combo_queimadas_layer_name(self):
        idx = self.__ignicao_combo_queimadas.currentIndex()
        if idx == 0:
            return None
        else:
            return self.__ignicao_combo_queimadas.itemText(idx)

    def apply_model(self, layer, weight):
        start_time = datetime.now()
        str_start_time = start_time.strftime(self.pt_br_format)
        self.logger.info('Running Ignicao model at {}...'.format(str_start_time))

        field_name = self.params['equation_field']
        writer = layer.dataProvider()

        idx = layer.fieldNameIndex(field_name)
        if idx != -1:
            writer.deleteAttributes([idx])
            layer.updateFields()

        writer.addAttributes([QgsField(field_name, QVariant.Double, '', 24, 15)])
        layer.updateFields()

        last_progress = 0
        total = 100.0 / layer.featureCount() if layer.featureCount() > 0 else 1
        dlg, bar = QtHandler.progress_dialog(label='Applying model Ignicao...')

        constant = float(weight['constant'])
        weight_queima = float(weight['queima'])
        weight_energia = float(weight['energia'])
        weight_enterra = float(weight['enterra'])
        weight_altitude = float(weight['altitude'])
        weight_insolacao = float(weight['insolacao'])
        weight_tmax = float(weight['tmax'])
        weight_vven = float(weight['vven'])
        weight_lsat_gndvi = float(weight['lsat_gndvi'])
        weight_lsat_ndvi = float(weight['lsat_ndvi'])
        weight_ab_med = float(weight['ab_med'])
        weight_ab_dif = float(weight['ab_dif'])
        weight_dens_med = float(weight['dens_med'])
        weight_vol_med = float(weight['vol_med'])
        weight_uso_c01_p = float(weight['uso_c01_p'])
        weight_uso_c02_p = float(weight['uso_c02_p'])
        weight_uso_c03_p = float(weight['uso_c03_p'])
        weight_uso_c04_p = float(weight['uso_c04_p'])
        weight_uso_c05_p = float(weight['uso_c05_p'])
        weight_uso_c06_p = float(weight['uso_c06_p'])
        weight_uso_c07_p = float(weight['uso_c07_p'])
        weight_uso_c08_p = float(weight['uso_c08_p'])
        weight_uso_c09_p = float(weight['uso_c09_p'])
        weight_uso_c10_p = float(weight['uso_c10_p'])
        weight_uso_c11_p = float(weight['uso_c11_p'])
        weight_uso_c12_p = float(weight['uso_c12_p'])
        weight_uso_c13_p = float(weight['uso_c13_p'])
        weight_uso_c14_p = float(weight['uso_c14_p'])
        weight_uso_c15_p = float(weight['uso_c15_p'])
        weight_uso_c16_p = float(weight['uso_c16_p'])
        weight_uso_c17_p = float(weight['uso_c17_p'])
        weight_uso_c18_p = float(weight['uso_c18_p'])
        weight_uso_c19_p = float(weight['uso_c19_p'])
        weight_uso_c20_p = float(weight['uso_c20_p'])
        weight_uso_c21_p = float(weight['uso_c21_p'])
        weight_uso_c22_p = float(weight['uso_c22_p'])

        layer.startEditing()
        bar.setValue(1)
        for current, ft in enumerate(layer.getFeatures()):
            ft[field_name] = self.__get_equation_value(
                ft,
                constant,
                weight_queima,
                weight_energia,
                weight_enterra,
                weight_altitude,
                weight_insolacao,
                weight_tmax,
                weight_vven,
                weight_lsat_gndvi,
                weight_lsat_ndvi,
                weight_ab_med,
                weight_ab_dif,
                weight_dens_med,
                weight_vol_med,
                weight_uso_c01_p,
                weight_uso_c02_p,
                weight_uso_c03_p,
                weight_uso_c04_p,
                weight_uso_c05_p,
                weight_uso_c06_p,
                weight_uso_c07_p,
                weight_uso_c08_p,
                weight_uso_c09_p,
                weight_uso_c10_p,
                weight_uso_c11_p,
                weight_uso_c12_p,
                weight_uso_c13_p,
                weight_uso_c14_p,
                weight_uso_c15_p,
                weight_uso_c16_p,
                weight_uso_c17_p,
                weight_uso_c18_p,
                weight_uso_c19_p,
                weight_uso_c20_p,
                weight_uso_c21_p,
                weight_uso_c22_p
            )

            layer.updateFeature(ft)

            progress = int(current * total)
            if progress != last_progress and progress % 10 == 0:
                self.logger.debug('{}%'.format(str(progress)))
                bar.setValue(progress)
            last_progress = progress
        layer.commitChanges()

        if last_progress != 100:
            bar.setValue(100)

        bar.close()
        dlg.close()
        del dlg

        end_time = datetime.now()
        time_elapsed = end_time - start_time

        str_end_time = end_time.strftime(self.pt_br_format)
        self.logger.info('Summing up, done at {}! Time elapsed {}(hh:mm:ss.ms)'.format(str_end_time, time_elapsed))

    def __initial_components_states(self):
        # disable combo
        self.__ignicao_combo_lt.setEnabled(False)
        self.__ignicao_combo_grid.setEnabled(False)

        self.__ignicao_group_entradas_modelo.setEnabled(False)
        self.__ignicao_group_formula_saida.setEnabled(False)
        self.__ignicao_group_grid_saida.setEnabled(False)

        # uncheck radio
        self.__ignicao_checkbox_lt.setChecked(False)
        self.__ignicao_checkbox_grid.setChecked(False)
        self.__ignicao_checkbox_habilitar_entradas.setChecked(False)
        self.__ignicao_checkbox_habilitar_formula.setChecked(False)

        self.__create_fill_grid = False
        self.__fill_grid = False
        self.__apply_formula = False

    def __init_combobox(self, rasters_name, polygons_name):
        rasters_combo = {
            PLUGIN_IGNICAO_INSOLACAO: self.__ignicao_combo_insolacao,
            PLUGIN_IGNICAO_TEMPERATURA_MAXIMA: self.__ignicao_combo_temperatura_maxima,
            PLUGIN_IGNICAO_VELOCIDADE_VENTO: self.__ignicao_combo_velocidade_vento,
            PLUGIN_IGNICAO_GNDVI: self.__ignicao_combo_gndvi,
            PLUGIN_IGNICAO_NDVI: self.__ignicao_combo_ndvi,
            PLUGIN_IGNICAO_AREA_BASAL: self.__ignicao_combo_area_basal,
            PLUGIN_IGNICAO_DENSIDADE: self.__ignicao_combo_densidade,
            PLUGIN_IGNICAO_VOLUME: self.__ignicao_combo_volume,
            PLUGIN_IGNICAO_ALTITUDE: self.__ignicao_combo_altitude
        }

        polygons_combo = {
            PLUGIN_IGNICAO_CENSO_IBGE: self.__ignicao_combo_censo_ibge,
            PLUGIN_IGNICAO_USO_SOLO: self.__ignicao_combo_uso_solo,
            PLUGIN_IGNICAO_GRID: self.__ignicao_combo_grid
        }

        self.__qt_raster.init_combobox(rasters_name, **rasters_combo)
        self.__qt_vector.init_combobox(polygons_name, **polygons_combo)

    def __init_qt(self, rasters_name, lines_names, polygons_name, points_name):
        self.__initial_components_states()

        QtHandler.set_combobox(self.__ignicao_combo_insolacao, rasters_name, self.on_insolacao_change)
        QtHandler.set_combobox(self.__ignicao_combo_temperatura_maxima, rasters_name, self.on_temperatura_change)
        QtHandler.set_combobox(self.__ignicao_combo_velocidade_vento, rasters_name, self.on_velocidade_change)
        QtHandler.set_combobox(self.__ignicao_combo_gndvi, rasters_name, self.on_gndvi_change)
        QtHandler.set_combobox(self.__ignicao_combo_ndvi, rasters_name, self.on_indvi_change)
        QtHandler.set_combobox(self.__ignicao_combo_area_basal, rasters_name, self.on_area_basal_change)
        QtHandler.set_combobox(self.__ignicao_combo_densidade, rasters_name, self.on_densidade_change)
        QtHandler.set_combobox(self.__ignicao_combo_volume, rasters_name, self.on_volume_change)
        QtHandler.set_combobox(self.__ignicao_combo_altitude, rasters_name, self.on_altitude_change)

        QtHandler.set_combobox(self.__ignicao_combo_lt, lines_names, self.on_linha_transmissao_change)
        QtHandler.set_combobox(self.__ignicao_combo_queimadas, points_name, self.on_queimadas_change)

        QtHandler.set_combobox(self.__ignicao_combo_grid, polygons_name, self.on_grid_change)
        QtHandler.set_combobox(self.__ignicao_combo_censo_ibge, polygons_name, self.on_censo_ibge_change)
        QtHandler.set_combobox(self.__ignicao_combo_uso_solo, polygons_name, self.on_uso_solo_change)

        QtHandler.set_radio(self.__ignicao_checkbox_lt, self.on_lt_toggled)
        QtHandler.set_radio(self.__ignicao_checkbox_grid, self.on_grid_toggled)
        QtHandler.set_radio(self.__ignicao_checkbox_habilitar_entradas, self.on_entradas_toggled)
        QtHandler.set_radio(self.__ignicao_checkbox_habilitar_formula, self.on_formula_toggled)

    def on_insolacao_change(self, combo, index):
        self.__qt_raster.on_combobox_change(PLUGIN_IGNICAO_INSOLACAO, combo, index)

    def on_temperatura_change(self, combo, index):
        self.__qt_raster.on_combobox_change(PLUGIN_IGNICAO_TEMPERATURA_MAXIMA, combo, index)

    def on_velocidade_change(self, combo, index):
        self.__qt_raster.on_combobox_change(PLUGIN_IGNICAO_VELOCIDADE_VENTO, combo, index)

    def on_censo_ibge_change(self, combo, index):
        self.__qt_vector.on_combobox_change(PLUGIN_IGNICAO_CENSO_IBGE, combo, index)

    def on_uso_solo_change(self, combo, index):
        self.__qt_vector.on_combobox_change(PLUGIN_IGNICAO_USO_SOLO, combo, index)

    def on_gndvi_change(self, combo, index):
        self.__qt_raster.on_combobox_change(PLUGIN_IGNICAO_GNDVI, combo, index)

    def on_indvi_change(self, combo, index):
        self.__qt_raster.on_combobox_change(PLUGIN_IGNICAO_NDVI, combo, index)

    def on_area_basal_change(self, combo, index):
        self.__qt_raster.on_combobox_change(PLUGIN_IGNICAO_AREA_BASAL, combo, index)

    def on_densidade_change(self, combo, index):
        self.__qt_raster.on_combobox_change(PLUGIN_IGNICAO_DENSIDADE, combo, index)

    def on_volume_change(self, combo, index):
        self.__qt_raster.on_combobox_change(PLUGIN_IGNICAO_VOLUME, combo, index)

    def on_altitude_change(self, combo, index):
        self.__qt_raster.on_combobox_change(PLUGIN_IGNICAO_ALTITUDE, combo, index)

    def on_grid_change(self, combo, index):
        self.__qt_vector.on_combobox_change(PLUGIN_IGNICAO_GRID, combo, index)

    def on_lt_toggled(self, enabled):
        if enabled:
            self.__ignicao_combo_grid.setEnabled(False)
            self.__ignicao_checkbox_habilitar_formula.setEnabled(False)
            self.__ignicao_checkbox_grid.setChecked(False)

            self.__ignicao_combo_lt.setEnabled(True)
            self.__ignicao_group_entradas_modelo.setEnabled(False)
            self.__ignicao_group_grid_saida.setEnabled(True)

            self.__ignicao_checkbox_lt.setChecked(True)
            self.__ignicao_checkbox_habilitar_entradas.setChecked(False)
            self.__ignicao_checkbox_habilitar_entradas.setEnabled(False)

            self.__create_fill_grid = True
        else:
            self.__initial_components_states()

    def on_grid_toggled(self, enabled):
        if enabled:
            self.__ignicao_checkbox_lt.setChecked(False)
            self.__ignicao_combo_lt.setEnabled(False)
            self.__ignicao_group_entradas_modelo.setEnabled(False)

            self.__ignicao_group_grid_saida.setEnabled(True)
            self.__ignicao_combo_grid.setEnabled(True)
            self.__ignicao_group_grid_saida.setEnabled(False)

            self.__ignicao_checkbox_grid.setChecked(True)
            self.__ignicao_checkbox_habilitar_formula.setEnabled(True)
            self.__ignicao_checkbox_habilitar_formula.setChecked(False)

            self.__ignicao_checkbox_habilitar_entradas.setChecked(False)
            self.__ignicao_checkbox_habilitar_entradas.setEnabled(True)

            self.__fill_grid = True
        else:
            self.__initial_components_states()

    def on_entradas_toggled(self, enabled):
        if enabled:
            self.__ignicao_checkbox_habilitar_formula.setChecked(False)
            self.__ignicao_checkbox_habilitar_formula.setEnabled(False)
            self.__ignicao_group_formula_saida.setEnabled(False)
            self.__ignicao_group_entradas_modelo.setEnabled(True)

            self.__ignicao_group_grid_saida.setEnabled(False)
        else:
            self.__ignicao_checkbox_habilitar_formula.setChecked(False)
            self.__ignicao_checkbox_habilitar_formula.setEnabled(True)
            self.__ignicao_group_formula_saida.setEnabled(False)
            self.__ignicao_group_entradas_modelo.setEnabled(False)

            self.__ignicao_group_grid_saida.setEnabled(True)

        self.__apply_formula = False

    def on_formula_toggled(self, enabled):
        if enabled:
            self.__ignicao_checkbox_habilitar_formula.setChecked(True)
            self.__ignicao_checkbox_habilitar_formula.setEnabled(True)
            self.__ignicao_group_formula_saida.setEnabled(True)
            self.__ignicao_group_entradas_modelo.setEnabled(False)
            self.__apply_formula = True
        else:
            self.__ignicao_checkbox_habilitar_formula.setChecked(False)
            self.__ignicao_checkbox_habilitar_formula.setEnabled(True)
            self.__ignicao_group_formula_saida.setEnabled(False)
            self.__ignicao_group_entradas_modelo.setEnabled(True)
            self.__apply_formula = False
            
    def get_field_value(self, ft, field_name):
        field_value = 0.0
        try:
            if ft[field_name] != NULL:
                field_value = float(ft[field_name])
        except Exception:
            pass            
        return field_value;

    def __get_equation_value(self, ft,
                             constant,
                             weight_queima,
                             weight_energia,
                             weight_enterra,
                             weight_altitude,
                             weight_insolacao,
                             weight_tmax,
                             weight_vven,
                             weight_lsat_gndvi,
                             weight_lsat_ndvi,
                             weight_ab_med,
                             weight_ab_dif,
                             weight_dens_med,
                             weight_vol_med,
                             weight_uso_c01_p,
                             weight_uso_c02_p,
                             weight_uso_c03_p,
                             weight_uso_c04_p,
                             weight_uso_c05_p,
                             weight_uso_c06_p,
                             weight_uso_c07_p,
                             weight_uso_c08_p,
                             weight_uso_c09_p,
                             weight_uso_c10_p,
                             weight_uso_c11_p,
                             weight_uso_c12_p,
                             weight_uso_c13_p,
                             weight_uso_c14_p,
                             weight_uso_c15_p,
                             weight_uso_c16_p,
                             weight_uso_c17_p,
                             weight_uso_c18_p,
                             weight_uso_c19_p,
                             weight_uso_c20_p,
                             weight_uso_c21_p,
                             weight_uso_c22_p):

        try:
            queima = float(ft['queima'])
            energia = float(ft['energia'])
            enterra = float(ft['enterra'])
            altitude = float(ft['altitude'])
            insolacao = float(ft['insolacao'])
            tmax = float(ft['tmax'])
            vven = float(ft['vven'])
            lsat_gndvi = float(ft['lsat_gndvi'])
            lsat_ndvi = float(ft['lsat_ndvi'])
            ab_med = float(ft['ab_med'])
            ab_dif = float(ft['ab_dif'])
            dens_med = float(ft['dens_med'])
            vol_med = float(ft['vol_med'])
            uso_c01_p = self.get_field_value(ft, 'uso_c01_p')
            uso_c02_p = self.get_field_value(ft, 'uso_c02_p')
            uso_c03_p = self.get_field_value(ft, 'uso_c03_p')
            uso_c04_p = self.get_field_value(ft, 'uso_c04_p')
            uso_c05_p = self.get_field_value(ft, 'uso_c05_p')
            uso_c06_p = self.get_field_value(ft, 'uso_c06_p')
            uso_c07_p = self.get_field_value(ft, 'uso_c07_p')
            uso_c08_p = self.get_field_value(ft, 'uso_c08_p')
            uso_c09_p = self.get_field_value(ft, 'uso_c09_p')
            uso_c10_p = self.get_field_value(ft, 'uso_c10_p')
            uso_c11_p = self.get_field_value(ft, 'uso_c11_p')
            uso_c12_p = self.get_field_value(ft, 'uso_c12_p')
            uso_c13_p = self.get_field_value(ft, 'uso_c13_p')
            uso_c14_p = self.get_field_value(ft, 'uso_c14_p')
            uso_c15_p = self.get_field_value(ft, 'uso_c15_p')
            uso_c16_p = self.get_field_value(ft, 'uso_c16_p')
            uso_c17_p = self.get_field_value(ft, 'uso_c17_p')
            uso_c18_p = self.get_field_value(ft, 'uso_c18_p')
            uso_c19_p = self.get_field_value(ft, 'uso_c19_p')
            uso_c20_p = self.get_field_value(ft, 'uso_c20_p')
            uso_c21_p = self.get_field_value(ft, 'uso_c21_p')
            uso_c22_p = self.get_field_value(ft, 'uso_c22_p')

            x = ((constant) +
                 (queima * (weight_queima)) +
                 (energia * (weight_energia)) +
                 (enterra * (weight_enterra)) +
                 (altitude * weight_altitude) +
                 (insolacao * (weight_insolacao)) +
                 (tmax * (weight_tmax)) +
                 (vven * (weight_vven)) +
                 (lsat_gndvi * weight_lsat_gndvi) +
                 (lsat_ndvi * (weight_lsat_ndvi)) +
                 (ab_med * (weight_ab_med)) +
                 (ab_dif * (weight_ab_dif)) +
                 (dens_med * weight_dens_med) +
                 (vol_med * (weight_vol_med)) +
                 (uso_c01_p * (weight_uso_c01_p)) +
                 (uso_c02_p * (weight_uso_c02_p)) +
                 (uso_c03_p * (weight_uso_c03_p)) +
                 (uso_c04_p * (weight_uso_c04_p)) +
                 (uso_c05_p * (weight_uso_c05_p)) +
                 (uso_c06_p * (weight_uso_c06_p)) +
                 (uso_c07_p * (weight_uso_c07_p)) +
                 (uso_c08_p * (weight_uso_c08_p)) +
                 (uso_c09_p * (weight_uso_c09_p)) +
                 (uso_c10_p * (weight_uso_c10_p)) +
                 (uso_c11_p * (weight_uso_c11_p)) +
                 (uso_c12_p * (weight_uso_c12_p)) +
                 (uso_c13_p * (weight_uso_c13_p)) +
                 (uso_c14_p * (weight_uso_c14_p)) +
                 (uso_c15_p * (weight_uso_c15_p)) +
                 (uso_c16_p * (weight_uso_c16_p)) +
                 (uso_c17_p * (weight_uso_c17_p)) +
                 (uso_c18_p * (weight_uso_c18_p)) +
                 (uso_c19_p * (weight_uso_c19_p)) +
                 (uso_c20_p * (weight_uso_c20_p)) +
                 (uso_c21_p * (weight_uso_c21_p)) +
                 (uso_c22_p * (weight_uso_c22_p)))

            value = 1 / (1 + (exp(-1 * x)))
        except Exception as e:
            value = NULL
            self.logger.debug('Fail to calculate cell fid {}: {}'.format(str(ft.id()), str(e)))
        return value

    @staticmethod
    def on_linha_transmissao_change(combo, index):
        if index == 0:
            return

    @staticmethod
    def on_queimadas_change(combo, index):
        if index == 0:
            return
