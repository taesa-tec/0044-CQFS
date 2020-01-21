import sys
import logging

print('Python %s on %s' % (sys.version, sys.platform))

sys.path.extend(['C:\\Users\\heitor.carneiro\\.qgis2\\python\\plugins\\CQFS', 'C:/Users/heitor.carneiro/.qgis2/python/plugins/CQFS'])

if __name__ == '__main__' or __name__ == '__console__':
    logging.basicConfig(level=logging.INFO)

    from datetime import datetime
    from CQFS.src.reclassify import Reclassify
    from CQFS.src.reclass.propagacao_vegetacao_reclass import PropagacaoVegetacaoReclass
    from CQFS.src.layer_util import import_layer_qgis

    date_formatter = '%Y%m%d%H%M%S'
    timestamp = datetime.now().strftime(date_formatter)

    output_raster = r'D:\Projetos\0023.2016_TAESA\data\propagacao\tmp\vegetacao_reclass_{}.tif'.format(str(timestamp))
    base_raster = r'D:\Projetos\0023.2016_TAESA\data\propagacao\tmp\uso_solo_clipped.tif'
    reclass = PropagacaoVegetacaoReclass(base_raster, output_raster)

    re = Reclassify(reclass)
    re.apply()

    import_layer_qgis(output_raster)
