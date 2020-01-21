"""
https://gis.stackexchange.com/questions/54949/how-to-evaluate-raster-calculator-expressions-from-the-console
"""

from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

# get all layers
# QgsMapLayerRegistry.instance().mapLayers().values()

# get layer by name
# QgsMapLayerRegistry.instance().mapLayersByName("uso_solo_clipped")

# using iface
# iface.legendInterface().layers() # all layers
# iface.legendInterface().selectedLayers() # selected
# iface.activeLayer() # mouse selected

# set iface activeLayer
# https://gis.stackexchange.com/questions/71350/pyqgis-question-how-to-change-or-set-active-layer/71471

vegetacao = QgsMapLayerRegistry.instance().mapLayersByName('uso_solo_clipped')[0]
clinografia = QgsMapLayerRegistry.instance().mapLayersByName('clinografia_clipped')[0]
orientacao_vertente = QgsMapLayerRegistry.instance().mapLayersByName('orientacao_vertente_clipped')[0]
proximidade_estradas = QgsMapLayerRegistry.instance().mapLayersByName('rodovia_clipped')[0]
hipsometria = QgsMapLayerRegistry.instance().mapLayersByName('hipsom_clipped')[0]

output_raster = r'D:\Projetos\0023.2016_TAESA\data\propagacao\tmp\propagacao_19.tif'

layers = [vegetacao, clinografia, orientacao_vertente, proximidade_estradas, hipsometria]

band = 1

entries = []
for layer in layers:
    entry = QgsRasterCalculatorEntry()
    entry.ref = layer.name() + '@' + str(band)
    entry.raster = layer
    entry.bandNumber = band
    entries.append(entry)

elements = {
    'v': entries[0].ref,
    's': entries[1].ref,
    'a': entries[2].ref,
    'r': entries[3].ref,
    'e': entries[4].ref
}

expression_template = '1 + (100 * "{v}") + (30 * "{s}")+ (10 * "{a}") + (5 * "{r}") + (2 * "{e}")'
expression = expression_template.format(**elements)
print(expression)

base_layer = 'v'
base_layer = elements[base_layer].split('@')[0]
base_layer = QgsMapLayerRegistry.instance().mapLayersByName(base_layer)[0]

extent = base_layer.extent()
width = base_layer.width()
height = base_layer.height()

calc = QgsRasterCalculator(expression, output_raster, 'GTiff', extent, width, height, entries)
result = calc.processCalculation()

output_msg = [
    'Calculation successful.',
    'Error creating output data file.',
    'Error reading input layer.'
    'User canceled calculation.',
    'Error parsing formula.'
    'Error allocating memory for result.'
]

print(output_msg[result])
