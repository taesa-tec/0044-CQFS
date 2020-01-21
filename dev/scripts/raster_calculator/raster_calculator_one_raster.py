"""
https://gis.stackexchange.com/questions/193455/qgis-python-script-loop-for-raster-calculator/193480#193480
"""

##NoDATA Background=name
##Raster=multiple raster
##OUT=folder

import glob
import processing
from qgis.core import QgsMapLayerRegistry, QgsRasterLayer
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from PyQt4.QtCore import QFileInfo

# Split rasters
layers = Raster.split(';')
output_path = OUT + "/"
suffix = "_suffix.tif"

for ras in layers:
    # Get layer object
    lyr = processing.getObjectFromUri(ras)
    entries = []
    ras = QgsRasterCalculatorEntry()
    ras.ref = 'lyr@1'
    ras.raster = lyr
    ras.bandNumber = 1
    entries.append( ras )
    calc = QgsRasterCalculator( '(lyr@1 / lyr@1) * lyr@1', output_path + lyr.name() + suffix, 'GTiff', lyr.extent(), lyr.width(), lyr.height(), entries )
    calc.processCalculation()

for results in glob.glob(output_path + "*" + suffix):
    fileInfo = QFileInfo(results)
    path = fileInfo.filePath()
    baseName = fileInfo.baseName()
    layer = QgsRasterLayer(path, baseName)
    QgsMapLayerRegistry.instance().addMapLayer(layer)
