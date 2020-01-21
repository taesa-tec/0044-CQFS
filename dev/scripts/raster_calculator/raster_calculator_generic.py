"""
https://gis.stackexchange.com/questions/250107/minidump-with-qgis-raster-calculator-in-python-console?noredirect=1&lq=1
"""
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

l=iface.activeLayer()
a=l.extent()
b=l.width()
c=l.height()
rast = QgsRasterCalculatorEntry()
rast.ref = l.name() +'@1'
rast.raster = l
rast.bandNumber = 1
entries=[ rast ]

expression = '( (' + entries[0].ref + ' ) = 1 ) * 200 + ' + '( (' + entries[0].ref + ' ) != 1 ) *  ' + entries[0].ref
print expression

calc = QgsRasterCalculator( expression,
                            "/home/zeito/pyqgis_data/z.tif",
                            'GTiff',
                            a,
                            b,
                            c,
                            entries )

calc.processCalculation()
