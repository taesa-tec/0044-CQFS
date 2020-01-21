# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 
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

from constants import PLUGIN_RISCO_FOGO, PLUGIN_RISCO_FOGO_PROPAGACAO
from qt_handler import QtHandler
from cqfs_config import load_config
from layer_util import find_one_layer_by_name

__logger = logging.getLogger(PLUGIN_RISCO_FOGO)


class RiscoFogo(object):
    cqfs_config = load_config()
    logger = logging.getLogger(PLUGIN_RISCO_FOGO)
    proj4 = cqfs_config['global']['crs_proj4']
    params = cqfs_config[PLUGIN_RISCO_FOGO]
        
    def __init__(self, dlg, vectors_name, rasters_name):
        self.__qt = QtHandler()
        
        self.__combo_risco_fogo_raster_propagacao = dlg.combo_risco_fogo_raster_propagacao
        self.__combo_risco_fogo_grid_ignicao = dlg.combo_risco_fogo_grid_ignicao
        self.__line_saida_risco_tecnico = dlg.line_saida_risco_tecnico
        self.__btn_saida_risco_tecnico = dlg.btn_saida_risco_tecnico

        QtHandler.set_combobox(self.__combo_risco_fogo_raster_propagacao, rasters_name, self.on_raster_propagacao_change)
        QtHandler.set_combobox(self.__combo_risco_fogo_grid_ignicao, vectors_name, self.on_grid_ignicao_change)
        
        combo = { 
            PLUGIN_RISCO_FOGO_PROPAGACAO: self.__combo_risco_fogo_raster_propagacao
        }
        
        self.__qt.init_combobox(rasters_name, **combo)

    def destroy(self):
        self.__combo_risco_fogo_raster_propagacao.clear()
        self.__combo_risco_fogo_grid_ignicao.clear()
        self.__line_saida_risco_tecnico.clear()

        self.__qt.clear_combobox()

        self.__qt = None
        self.__combo_risco_fogo_raster_propagacao = None
        self.__combo_risco_fogo_grid_ignicao = None
        self.__line_saida_risco_tecnico = None
        self.__btn_saida_risco_tecnico = None


    @property
    def combo_name_by_layer_index(self):
        return self.__qt.combo_name_by_layer_index
    
    def on_raster_propagacao_change(self, combo, index):
        self.__qt.on_combobox_change(PLUGIN_RISCO_FOGO_PROPAGACAO, combo, index)
        
    @staticmethod
    def on_grid_ignicao_change(combo, index):
        if index == 0:
            return
