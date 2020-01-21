import os

from osgeo import ogr, osr
from math import ceil
from datetime import datetime
from qgis.core import *
from qgis.gui import QgsMapCanvas
from PyQt4.QtGui import *
from qgis_interface import QgisInterface

OGR_DRIVER_NAME = 'ESRI Shapefile'


def create_grid(input_gridfn, output_gridfn, xmin, xmax, ymin, ymax, grid_height, grid_width):
    xmin = float(xmin)
    xmax = float(xmax)
    ymin = float(ymin)
    ymax = float(ymax)
    grid_width = float(grid_width)
    grid_height = float(grid_height)

    # get rows
    rows = ceil((ymax - ymin) / grid_height)
    # get columns
    cols = ceil((xmax - xmin) / grid_width)

    # start grid cell envelope
    ring_xleft_origin = xmin
    ring_xright_origin = xmin + grid_width
    ring_ytop_origin = ymax
    ring_ybottom_origin = ymax - grid_height

    # create output file
    if os.path.exists(output_gridfn):
        os.remove(output_gridfn)

    ogr_driver = ogr.GetDriverByName(OGR_DRIVER_NAME)

    base_data_source = ogr.Open(input_gridfn)
    bbox_layer = base_data_source.GetLayer()
    bbox_feature = bbox_layer.GetNextFeature()
    bbox_geom = bbox_feature.GetGeometryRef()
    bbox_srs = bbox_layer.GetSpatialRef()

    out_data_source = ogr_driver.CreateDataSource(output_gridfn)
    out_layer = out_data_source.CreateLayer(output_gridfn, bbox_srs, ogr.wkbPolygon)
    feature_defn = out_layer.GetLayerDefn()

    progress_cont = 0.0
    progress_previous = 0.0
    progress_total = float(cols)

    length = 50
    fill = '#'

    print('Creating a grid with {} rows and {} cols ({} cells)'.format(rows, cols, rows * cols))

    # create grid cells
    countcols = 0
    while countcols < cols:
        countcols += 1

        # reset envelope for rows
        ring_ytop = ring_ytop_origin
        ring_ybottom = ring_ybottom_origin

        countrows = 0
        while countrows < rows:
            countrows += 1

            geom = create_polygon(ring_xleft_origin, ring_xright_origin, ring_ybottom, ring_ytop)

            if geom.Intersects(bbox_geom):
                # add new geom to layer
                add_geom_to_layer(feature_defn, out_layer, geom)

            # new envelope for next geom
            ring_ytop = ring_ytop - grid_height
            ring_ybottom = ring_ybottom - grid_height

        # new envelope for next geom
        ring_xleft_origin = ring_xleft_origin + grid_width
        ring_xright_origin = ring_xright_origin + grid_width

        progress_cont += 1
        progress = 100 * (progress_cont / progress_total)

        if round(progress, 1) != round(progress_previous, 1):
            percent = ('{0:.' + str(1) + 'f}').format(progress)
            filled_length = int(length * progress_cont // progress_total)
            bar = fill * filled_length + '-' * (length - filled_length)
            out = '%s |%s| %s%% %s' % ('Progress:', bar, percent, 'Complete')
            print(out)

        progress_previous = progress

    # Save and close DataSources
    del out_data_source
    del bbox_feature
    del base_data_source


def add_geom_to_layer(feature_defn, out_layer, poly):
    out_feature = ogr.Feature(feature_defn)
    out_feature.SetGeometry(poly)
    out_layer.CreateFeature(out_feature)
    del out_feature


def create_polygon(ring_xleft_origin, ring_xright_origin, ring_ybottom, ring_ytop):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(ring_xleft_origin, ring_ytop)
    ring.AddPoint(ring_xright_origin, ring_ytop)
    ring.AddPoint(ring_xright_origin, ring_ybottom)
    ring.AddPoint(ring_xleft_origin, ring_ybottom)
    ring.AddPoint(ring_xleft_origin, ring_ytop)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    return poly


if __name__ == '__main__' or __name__ == '__console__':
    app = QApplication([])
    QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 2.18\apps\qgis', True)
    QgsApplication.initQgis()

    canvas = QgsMapCanvas()
    iface = QgisInterface(canvas)

    output_source = r'D:\Projetos\0023.2016_TAESA\data\iginicao\tmp\grid.shp'

    base_layer_source = r'D:\Projetos\0023.2016_TAESA\data\iginicao\tmp\buffer.shp'
    basename = os.path.splitext(os.path.basename(base_layer_source))[0]

    input_layer = QgsVectorLayer(base_layer_source, basename, 'ogr')

    '''
    https://gis.stackexchange.com/questions/245811/getting-layer-extent-in-pyqgis
    https://gis.stackexchange.com/questions/130794/getting-shapefile-extent-from-standalone-pyqgis-script
    https://gis.stackexchange.com/questions/224930/how-to-select-polygons-which-contain-at-least-one-point-with-spatial-index
    https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html
    https://gis.stackexchange.com/questions/174622/how-to-access-shapefile-metadata-and-metatypes-information-using-ogr
    '''

    ext = input_layer.extent()
    xmin = ext.xMinimum()
    xmax = ext.xMaximum()
    ymin = ext.yMinimum()
    ymax = ext.yMaximum()
    cell_size = 500

    if int(input_layer.featureCount()) != 1:
        msg = 'Buffer "{}" is not valid, has more than one feature.'.format(input_layer.name())
        print(msg)
        raise RuntimeError(msg)

    input_source = input_layer.source()

    print('Starts create grid...')
    start_time = datetime.now()

    create_grid(input_layer.source(), output_source, xmin, xmax, ymin, ymax, cell_size, cell_size)

    end_time = datetime.now()
    time_elapsed = end_time - start_time

    pt_br_format = '%d/%m/%Y %H:%M'
    str_end_time = end_time.strftime(pt_br_format)
    print('Summing up, script "{}" done at {}! Time elapsed {}(hh:mm:ss.ms)'.format(__file__, str_end_time, time_elapsed))

    QgsApplication.exitQgis()
    app.exit()
