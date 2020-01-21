layer = iface.activeLayer() #in my case, a 20x20 raster

provider = layer.dataProvider()

extent = provider.extent()

rows = layer.height()
cols = layer.width()

block = provider.block(1, extent, cols, rows)

for i in range(rows):
    for j in range(cols):
        value = block.value(i,j)
        if value != -9999.0:
            print(value)

print('done')
