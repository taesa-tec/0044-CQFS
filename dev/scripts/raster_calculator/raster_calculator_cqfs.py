import sys
print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['C:\\Users\\heitor.carneiro\\.qgis2\\python\\plugins\\CQFS','C:/Users/heitor.carneiro/.qgis2/python/plugins/CQFS'])

import logging
from re import findall

from qgis.core import QgsMapLayerRegistry
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

from src.constants import PLUGIN_PROPAGACAO
from src.constants import PLUGIN_PROPAGACAO_HIPSOMETRIA
from src.constants import PLUGIN_PROPAGACAO_CLINOGRAFIA
from src.constants import PLUGIN_PROPAGACAO_ORIENTACAO_VERTENTE
from src.constants import PLUGIN_PROPAGACAO_PROXIMIDADE_ESTRADAS
from src.constants import PLUGIN_PROPAGACAO_VEGETACAO

from src.cqfs_config import load_config, tmp_filename_without_extension, strtimestamp
from src.layer_util import find_one_layer_by_name
from src.layer_util import import_layer_qgis
from src.layer_util import has_correct_crs
from src.layer_util import is_raster_valid as raster_ok
from src.layer_util import raster_calculator_from_config
from src.layer_util import set_layer_style
from src.qt_handler import QtHandler
from src.reclass.propagacao_clinografia_reclass import PropagacaoClinografiaReclass
from src.reclass.propagacao_hipsometria_reclass import PropagacaoHipsometriaReclass
from src.reclass.propagacao_model_reclass import PropagacaoModelReclass
from src.reclass.propagacao_orientacao_vertente_reclass import PropagacaoOrientacaoVertenteReclass
from src.reclass.propagacao_proximidade_estradas_reclass import PropagacaoProximidadeEstradasReclass
from src.reclass.propagacao_vegetacao_reclass import PropagacaoVegetacaoReclass
from src.reclassify import Reclassify


def apply_model(params, vegetacao, clinografia, orientacao_vertente, proximidade_estradas, hipsometria,
                output_raster):
    """
    Apply propagacao model.

    :param vegetacao: A string with the layer name (layer.name()).
    :param clinografia: A string with the layer name (name.name()).
    :param orientacao_vertente: A string with the layer path (layer.name()).
    :param proximidade_estradas: A string with layer name (layer.name()).
    :param hipsometria: A string with the layer name (layer.name()).
    :param output_raster: A string with the layer output path.
    :return: QgsRasterLayer
    """

    _, bar = QtHandler.progress_dialog(label='apply_model...')

    expression_template = params['expression']
    default_band = params['expression_default_band']
    expression_base_layer = params['expression_base_layer']

    print(expression_template)
    print(expression_base_layer)

    bar.setValue(10)

    layers_name = [vegetacao, clinografia, orientacao_vertente, proximidade_estradas, hipsometria]
    expression_alias = findall(r'\{(.*?)\}', expression_template)

    print(layers_name)
    print(expression_alias)

    bar.setValue(20)

    idx = expression_alias.index(expression_base_layer)
    base_layer_name = layers_name[idx]

    tmp_output_raster = tmp_filename_without_extension() + '.tif'
    print(tmp_output_raster)

    bar.setValue(40)

    code, msg = raster_calculator_from_config(layers_name, expression_alias, expression_template, base_layer_name,
                                              tmp_output_raster, default_band)

    bar.setValue(80)

    import_layer_qgis(tmp_output_raster, suffix=strtimestamp())
    bar.setValue(100)

    return code, msg


if __name__ == '__console__':
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    config = config[PLUGIN_PROPAGACAO]

    v1, v2 = apply_model(
        config,
        'uso_solo',
        'clino',
        'aspect',
        'rodovia',
        'hipsom_100004',
        r'C:\Users\heitor.carneiro\.qgis2\python\plugins\CQFS\dev\scripts\raster_calculator\output\output.tif'
    )

    print(v1, v2)

    # vegetacao = QgsMapLayerRegistry.instance().mapLayersByName('uso_solo')[0]
    # clinografia = QgsMapLayerRegistry.instance().mapLayersByName('clino')[0]
    # orientacao_vertente = QgsMapLayerRegistry.instance().mapLayersByName('aspect')[0]
    # proximidade_estradas = QgsMapLayerRegistry.instance().mapLayersByName('rodovia')[0]
    # hipsometria = QgsMapLayerRegistry.instance().mapLayersByName('hipsom_100004')[0]
    #
    # output_raster = r'C:\Users\heitor.carneiro\.qgis2\python\plugins\CQFS\dev\scripts\raster_calculator\output\output.tif'
    #
    # layers = [vegetacao, clinografia, orientacao_vertente, proximidade_estradas, hipsometria]
    #
    # band = 1
    #
    # entries = []
    # for layer in layers:
    #     entry = QgsRasterCalculatorEntry()
    #     entry.ref = layer.name() + '@' + str(band)
    #     entry.raster = layer
    #     entry.bandNumber = band
    #     entries.append(entry)
    #
    # expression = '1 + (100 * "uso_solo@1") + (30 * "clino@1")+ (10 * "aspect@1") + (5 * "rodovia@1") + (2 * "hipsom_100004@1")'
    # print(expression)
    #
    # base_layer = vegetacao
    #
    # extent = base_layer.extent()
    # width = base_layer.width()
    # height = base_layer.height()
    #
    # calc = QgsRasterCalculator(expression, output_raster, 'GTiff', extent, width, height, entries)
    # result = calc.processCalculation()
    #
    # output_msg = [
    #     'Calculation successful.',
    #     'Error creating output data file.',
    #     'Error reading input layer.'
    #     'User canceled calculation.',
    #     'Error parsing formula.'
    #     'Error allocating memory for result.'
    # ]
    #
    # print(output_msg[result])
