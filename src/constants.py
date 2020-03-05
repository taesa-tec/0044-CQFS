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
import os

CQFS_PATH = os.path.split(os.path.dirname(__file__))[0]
CQFS_CONFIG = os.path.join(CQFS_PATH, 'cqfs.yaml')
CQFS_STYLE = os.path.join(CQFS_PATH, 'resources', 'style')

PLUGIN_PROPAGACAO = 'propagacao'
PLUGIN_PROPAGACAO_HIPSOMETRIA = 'hipsometria'
PLUGIN_PROPAGACAO_CLINOGRAFIA = 'clinografia'
PLUGIN_PROPAGACAO_ORIENTACAO_VERTENTE = 'orientacao_vertente'
PLUGIN_PROPAGACAO_PROXIMIDADE_ESTRADAS = 'proximidade_estradas'
PLUGIN_PROPAGACAO_VEGETACAO = 'vegetacao'

PLUGIN_IGNICAO = 'ignicao'
PLUGIN_IGNICAO_INSOLACAO = 'insolacao'
PLUGIN_IGNICAO_TEMPERATURA_MAXIMA = 'temperatura_maxima'
PLUGIN_IGNICAO_VELOCIDADE_VENTO = 'velocidade_vento'
PLUGIN_IGNICAO_CENSO_IBGE = 'censo_ibge'
PLUGIN_IGNICAO_USO_SOLO = 'uso_solo'
PLUGIN_IGNICAO_GNDVI = 'gndvi'
PLUGIN_IGNICAO_NDVI = 'ndvi'
PLUGIN_IGNICAO_AREA_BASAL = 'area_basal'
PLUGIN_IGNICAO_DENSIDADE = 'densidade'
PLUGIN_IGNICAO_VOLUME = 'volume'
PLUGIN_IGNICAO_QUEIMADAS = 'queimadas'
PLUGIN_IGNICAO_ALTITUDE = 'altitude'
PLUGIN_IGNICAO_GRID = 'ignicao_grid'

PLUGIN_VULNERABILIDADE = 'vulnerabilidade'
PLUGIN_VULNERABILIDADE_TORRE = 'torres'
PLUGIN_VULNERABILIDADE_VAO = 'vao'
PLUGIN_VULNERABILIDADE_PC = 'ponto_critico'

PLUGIN_RISCO_FOGO = 'riscofogo'
PLUGIN_RISCO_FOGO_PROPAGACAO = 'propagacao'
PLUGIN_RISCO_FOGO_IGNICAO = 'ignicao'

PLUGIN_CRITICIDADE = 'criticidade'
