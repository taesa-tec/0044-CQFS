# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-09-28
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
from .handler import Handler
from ...src.constants import PLUGIN_IGNICAO
from .ignicao.create_handler import CreateHandler
from .ignicao.fill_handler import FillHandler
from .ignicao.formula_handler import FormulaHandler


class IgnicaoHandler(Handler):

    def handle(self, **kwargs):
        cqfs = kwargs['cqfs']

        ignicao = cqfs.ignicao
        if ignicao.is_create:
            handler = CreateHandler()
            handler.handle(
                cqfs=cqfs,
                line_saida_modelo=cqfs.dlg.ignicao_line_saida_modelo,
                combo_vector=cqfs.dlg.ignicao_combo_lt,
                layers=kwargs['layers'],
                plugin_name=PLUGIN_IGNICAO,
                proj4=ignicao.proj4
            )
        elif ignicao.is_formula:
            handler = FormulaHandler()
            handler.handle(
                cqfs=cqfs,
                layers=kwargs['layers'],
                polygons_name=kwargs['polygons_name'],
                points_name=kwargs['points_name'],
                combo_vector=cqfs.dlg.ignicao_combo_grid,
                msgselecione='Selecione o grid.',
                msgprojecao='Grid nao possui projecao experada "{}".'
            )
        elif ignicao.is_fill:
            handler = FillHandler()
            handler.handle(
                cqfs=cqfs,
                layers=kwargs['layers'],
                rasters_name=kwargs['rasters_name'],
                polygons_name=kwargs['polygons_name'],
                points_name=kwargs['points_name'],
                combo_vector=cqfs.dlg.ignicao_combo_grid,
                msgselecione='Selecione o grid.',
                msgprojecao='Grid nao possui projecao experada "{}".'
            )
        else:
            ignicao.logger.error('Status is not defined.')
            cqfs.show_error('Selecione uma operacao valida para Ignicao.')
