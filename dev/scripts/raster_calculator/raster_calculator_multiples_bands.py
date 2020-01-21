"""
https://gis.stackexchange.com/questions/54949/how-to-evaluate-raster-calculator-expressions-from-the-console
"""

from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

entries = []
# Define band1
boh1 = QgsRasterCalculatorEntry()
boh1.ref = 'boh@1'
boh1.raster = bohLayer
boh1.bandNumber = 1
entries.append( boh1 )

# Define band2
boh2 = QgsRasterCalculatorEntry()
boh2.ref = 'boh@2'
boh2.raster = bohLayer
boh2.bandNumber = 2
entries.append( boh2 )

# Process calculation with input extent and resolution
calc = QgsRasterCalculator( 'boh@1 + boh@2', '/home/user/outputfile.tif', 'GTiff', bohLayer.extent(), bohLayer.width(), bohLayer.height(), entries )
calc.processCalculation()
