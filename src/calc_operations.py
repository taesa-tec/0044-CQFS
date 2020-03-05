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
import logging
import math

from PyQt4.QtCore import QVariant
from cqfs_config import load_config, tmp_filename_without_extension
from qgis._core import QgsField
from layer_util import set_layer_style, has_attributes
from ..src.qt_handler import QtHandler

__logger = logging.getLogger('calc_operations')
__config = load_config()


def calc(plugin_name, progress, layer):
    __logger.info('Start calc')

    params = __config[plugin_name]

    __logger.info(layer)

    fields = [str(field.name()) for field in layer.pendingFields()]

    pr = layer.dataProvider()

    if params['att_rup_ff'] not in fields:
        pr.addAttributes([QgsField(params['att_rup_ff'], QVariant.Double)])

    if params['att_rup_ft'] not in fields:
        pr.addAttributes([QgsField(params['att_rup_ft'], QVariant.Double)])

    if params['att_vul_ff'] not in fields:
        pr.addAttributes([QgsField(params['att_vul_ff'], QVariant.String)])

    if params['att_vul_ft'] not in fields:
        pr.addAttributes([QgsField(params['att_vul_ft'], QVariant.String)])

    if params['att_vulner'] not in fields:
        pr.addAttributes([QgsField(params['att_vulner'], QVariant.String)])

    if params['att_buffer_dist'] not in fields:
        pr.addAttributes([QgsField(params['att_buffer_dist'], QVariant.Double)])

    layer.updateFields()

    layer.startEditing()
    for feature in layer.getFeatures():
        alt_veg = feature[params['att_alt_veg']]
        alt_pc = feature[params['att_alt_pc']]

        gap = calc_gap(alt_veg, alt_pc)

        poder_calorifico = feature[params['att_poder_calorifico']]
        pressao_atm = feature[params['att_pressao_atm']]
        densidade_ar = calc_densidade_ar(pressao_atm, gap)

        tensao_ruptura_ft = calc_tensao_ruptura_ft(densidade_ar, gap)

        dist_fases = feature[params['att_dist_fases']]
        tensao_ruptura_ff = calc_tensao_ruptura_ff(pressao_atm, dist_fases, gap)

        layer.changeAttributeValue(feature.id(), layer.fieldNameIndex(params['att_rup_ff']), tensao_ruptura_ft)
        layer.changeAttributeValue(feature.id(), layer.fieldNameIndex(params['att_rup_ft']), tensao_ruptura_ff)

        vulner_FF = classificacao_ff(tensao_ruptura_ff, plugin_name)
        vulner_FT = classificacao_ft(tensao_ruptura_ft, plugin_name)

        layer.changeAttributeValue(feature.id(), layer.fieldNameIndex(params['att_vul_ff']), vulner_FF)
        layer.changeAttributeValue(feature.id(), layer.fieldNameIndex(params['att_vul_ft']), vulner_FT)

        classificacao = classificacao_vulnerabilidade(vulner_FF, vulner_FT, plugin_name)

        layer.changeAttributeValue(feature.id(), layer.fieldNameIndex(params['att_vulner']), classificacao)

        buffer_distance = calc_buffer_distance(gap)

        layer.changeAttributeValue(feature.id(), layer.fieldNameIndex(params['att_buffer_dist']), buffer_distance)

    layer.commitChanges()

    style = params['style']
    set_layer_style(layer, plugin_name, style['vulnerabilidade'])

    return


def calc_gap(alt_veg, alt_pc):
    result = alt_pc - alt_veg
    if result <= 0:
        return 1
    else:
        return result


def calc_densidade_ar(pressao_atm, gap):
    return (293 * pressao_atm) / (760 * (273 + calc_temperatura(gap)))

def calc_temperatura(gap):
    n = gap
    soma_t = 0
    while n > 1:
        soma_t += calc_gradiente_temp(n)
        n -= 1
    soma_t += 900
    return soma_t / (math.floor(gap) + 1)


def calc_gradiente_temp(alt_pc):
    return 976.94 * alt_pc ** (-0.992)


def calc_tensao_ruptura_ft(densidade, gap):
    return 27.2 * densidade * 12.5 * (1 + (0.54 / math.sqrt(densidade * 12.5))) * (gap * 100 / 12.5) / (
        0.25 * (gap * 100 / 12.5 + 1 + math.sqrt((gap * 100 / 12.5 + 1) ** 2 + 8)))


def calc_tensao_ruptura_ff(pressao_atm, dist_fase, gap):
    return 27.2 * (293 * pressao_atm) / (760 * (273 + (976.94 * (gap ** (-0.992))))) * 12.5 * (
        1 + (0.54 / math.sqrt((293 * pressao_atm) / (760 * (273 + (976.94 * (gap ** (-0.992))))) * 12.5))) * (
               dist_fase * 100 / 12.5) / (
               0.25 * (dist_fase * 100 / 12.5 + 1 + math.sqrt((dist_fase * 100 / 12.5 + 1) ** 2 + 8)))


def calc_buffer_distance(gap):
    distance = (((15.877 ** 2) - (gap ** 2)) - 5)
    if distance < 0:
        distance = 1

    return math.sqrt(distance)


def classificacao_ff(ruptura_ff, plugin_name):
    params = __config[plugin_name]

    if ruptura_ff <= 600:
        return params['classif_alta']

    elif 600 < ruptura_ff <= 650:
        return params['classif_media']

    else:
        return params['classif_baixa']


def classificacao_ft(ruptura_ft, plugin_name):
    params = __config[plugin_name]

    if ruptura_ft <= 348:
        return params['classif_alta']

    elif 348 < ruptura_ft <= 380:
        return params['classif_media']

    else:
        return params['classif_baixa']


def classificacao_vulnerabilidade(vulner_FF, vulner_FT, plugin_name):
    params = __config[plugin_name]

    if vulner_FF == params['classif_alta'] and vulner_FT == params['classif_alta']:
        return params['classif_alta']

    elif vulner_FF == params['classif_media'] and vulner_FT == params['classif_alta']:
        return params['classif_alta']

    elif vulner_FF == params['classif_baixa'] and vulner_FT == params['classif_alta']:
        return params['classif_alta']

    elif vulner_FF == params['classif_alta'] and vulner_FT == params['classif_media']:
        return params['classif_alta']

    elif vulner_FF == params['classif_media'] and vulner_FT == params['classif_media']:
        return params['classif_media']

    elif vulner_FF == params['classif_baixa'] and vulner_FT == params['classif_media']:
        return params['classif_media']

    elif vulner_FF == params['classif_alta'] and vulner_FT == params['classif_baixa']:
        return params['classif_alta']

    elif vulner_FF == params['classif_media'] and vulner_FT == params['classif_baixa']:
        return params['classif_media']

    elif vulner_FF == params['classif_baixa'] and vulner_FT == params['classif_baixa']:
        return params['classif_baixa']


def classificar_criticidade(zonal_layer, vulnerabilidade_layer, plugin_criticidade, plugin_vulnerabilidade):
    __logger.info('Start classify criticidade')

    _, bar = QtHandler.progress_dialog(label='Classifying Risk...')

    params_vulnerabilidade = __config[plugin_vulnerabilidade]
    params_criticidade = __config[plugin_criticidade]

    fields = [str(field.name()) for field in zonal_layer.pendingFields()]
    zonal_features = {}
    for zonal_feature in zonal_layer.getFeatures():
        zonal_features[int(zonal_feature.id())] = zonal_feature

    bar.setValue(20)

    pr = zonal_layer.dataProvider()

    if params_criticidade['att_cls_criticidade'] not in fields:
        pr.addAttributes([QgsField(params_criticidade['att_cls_criticidade'], QVariant.String)])

    bar.setValue(40)
    zonal_layer.updateFields()

    zonal_layer.startEditing()
    for feature in vulnerabilidade_layer.getFeatures():
        fid = int(feature.id())
        if fid not in zonal_features:
            continue
        vulnerabilidade = feature[params_vulnerabilidade['att_vulner']]
        zonal_feat = zonal_features[int(feature.id())]
        risco = zonal_feat[params_criticidade['att_cls_criticidade']]

        criticidade = classificacao_criticidade(vulnerabilidade, risco, plugin_criticidade, plugin_vulnerabilidade)

        zonal_layer.changeAttributeValue(feature.id(),
                                         zonal_layer.fieldNameIndex(params_criticidade['att_cls_criticidade']),
                                         criticidade)

    zonal_layer.commitChanges()

    bar.setValue(70)

    style = params_criticidade['style']
    set_layer_style(zonal_layer, plugin_criticidade, style['criticidade'])

    bar.setValue(100)

    return None, zonal_layer


def classificacao_criticidade(vulnerabilidade, risco, plugin_criticidade, plugin_vulnerabilidade):
    params_vulnerabilidade = __config[plugin_vulnerabilidade]
    params_criticidade = __config[plugin_criticidade]

    if vulnerabilidade == params_vulnerabilidade['classif_baixa'] and risco == params_criticidade[
        'classif_muito_baixa']:
        return params_criticidade['classif_baixa']

    elif vulnerabilidade == params_vulnerabilidade['classif_baixa'] and risco == params_criticidade['classif_baixa']:
        return params_criticidade['classif_baixa']

    elif vulnerabilidade == params_vulnerabilidade['classif_baixa'] and risco == params_criticidade['classif_media']:
        return params_criticidade['classif_media']

    elif vulnerabilidade == params_vulnerabilidade['classif_baixa'] and risco == params_criticidade['classif_alta']:
        return params_criticidade['classif_media']

    elif vulnerabilidade == params_vulnerabilidade['classif_baixa'] and risco == params_criticidade[
        'classif_muito_alta']:
        return params_criticidade['classif_media']

    elif vulnerabilidade == params_vulnerabilidade['classif_media'] and risco == params_criticidade[
        'classif_muito_baixa']:
        return params_criticidade['classif_baixa']

    elif vulnerabilidade == params_vulnerabilidade['classif_media'] and risco == params_criticidade['classif_baixa']:
        return params_criticidade['classif_media']

    elif vulnerabilidade == params_vulnerabilidade['classif_media'] and risco == params_criticidade['classif_media']:
        return params_criticidade['classif_media']

    elif vulnerabilidade == params_vulnerabilidade['classif_media'] and risco == params_criticidade['classif_alta']:
        return params_criticidade['classif_alta']

    elif vulnerabilidade == params_vulnerabilidade['classif_media'] and risco == params_criticidade[
        'classif_muito_alta']:
        return params_criticidade['classif_alta']

    elif vulnerabilidade == params_vulnerabilidade['classif_alta'] and risco == params_criticidade[
        'classif_muito_baixa']:
        return params_criticidade['classif_media']

    elif vulnerabilidade == params_vulnerabilidade['classif_alta'] and risco == params_criticidade['classif_baixa']:
        return params_criticidade['classif_media']

    elif vulnerabilidade == params_vulnerabilidade['classif_alta'] and risco == params_criticidade['classif_media']:
        return params_criticidade['classif_alta']

    elif vulnerabilidade == params_vulnerabilidade['classif_alta'] and risco == params_criticidade['classif_alta']:
        return params_criticidade['classif_alta']

    elif vulnerabilidade == params_vulnerabilidade['classif_alta'] and risco == params_criticidade[
        'classif_muito_alta']:
        return params_criticidade['classif_alta']
