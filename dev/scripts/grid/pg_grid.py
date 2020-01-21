import argparse
import logging
import os
import time
from math import ceil

import gdal
import ogr
import osr
from osgeo.gdalconst import *


def progress_bar(iteration, total, prefix='Progress:', suffix='Complete', decimals=1, length=100, fill='#'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)

    out = '\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix)
    logging.info(out)


def extent(raster):
    src_ds = gdal.Open(raster, GA_ReadOnly)
    geoTransform = src_ds.GetGeoTransform()

    width = geoTransform[1]
    height = geoTransform[5]
    xmin = geoTransform[0]
    ymax = geoTransform[3]
    xmax = xmin + width * src_ds.RasterXSize
    ymin = ymax + height * src_ds.RasterYSize

    return {
        'xmin': xmin,
        'xmax': xmax,
        'ymin': ymin,
        'ymax': ymax,
        'width': width,
        'height': -height
    }


def grid(outputGridfn, xmin, xmax, ymin, ymax, gridHeight, gridWidth, layer=None, boundingBoxGeom=None):
    rows = ceil((ymax - ymin) / gridHeight)
    cols = ceil((xmax - xmin) / gridWidth)
    logging.info("Creating a grid with {} rows and {} cols ({} cells)".format(rows, cols, rows * cols))

    ringXleftOrigin = xmin
    ringXrightOrigin = xmin + gridWidth
    ringYtopOrigin = ymax
    ringYbottomOrigin = ymax - gridHeight
    logging.info("Starting grid cell envelope: {}(ringXleftOrigin), {}(ringXrightOrigin), {}(ringYtopOrigin), "
                 "{}(ringYbottomOrigin)".format(ringXleftOrigin, ringXrightOrigin, ringYtopOrigin, ringYbottomOrigin))

    if not layer:
        defaultDriver = "ESRI Shapefile"
        logging.info("Using default layer type: {}".format(defaultDriver))
        outDriver = ogr.GetDriverByName(defaultDriver)
        if os.path.exists(outputGridfn):
            os.remove(outputGridfn)
        outDataSource = outDriver.CreateDataSource(outputGridfn)
        outLayer = outDataSource.CreateLayer(outputGridfn, geom_type=ogr.wkbPolygon)
    else:
        logging.info("Using user-defined layer type")
        outLayer = layer

    # LayerDefn
    featureDefn = outLayer.GetLayerDefn()

    # create grid cells
    progress_cont = 0
    progress_bar(progress_cont, cols)
    transaction_cont = 0
    countcols = 0

    while countcols < cols:
        countcols += 1

        # reset envelope for rows
        ringYtop = ringYtopOrigin
        ringYbottom = ringYbottomOrigin
        countrows = 0

        while countrows < rows:
            countrows += 1
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(ringXleftOrigin, ringYtop)
            ring.AddPoint(ringXrightOrigin, ringYtop)
            ring.AddPoint(ringXrightOrigin, ringYbottom)
            ring.AddPoint(ringXleftOrigin, ringYbottom)
            ring.AddPoint(ringXleftOrigin, ringYtop)
            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)

            # add new geom to layer
            if not boundingBoxGeom or poly.Intersects(boundingBoxGeom):
                if transaction_cont == 0:
                    outLayer.StartTransaction()

                outFeature = ogr.Feature(featureDefn)
                outFeature.SetGeometry(poly)
                outLayer.CreateFeature(outFeature)

                if transaction_cont == 1000:
                    outLayer.CommitTransaction()
                    transaction_cont = 0

                transaction_cont += 1
                del outFeature

            # new envelope for next poly
            ringYtop = ringYtop - gridHeight
            ringYbottom = ringYbottom - gridHeight

        # new envelope for next poly
        ringXleftOrigin = ringXleftOrigin + gridWidth
        ringXrightOrigin = ringXrightOrigin + gridWidth

        progress_cont += 1
        progress_bar(progress_cont, cols)

    if transaction_cont > 0:
        logging.info("Closing transaction with {} records".format(transaction_cont))
        outLayer.CommitTransaction()
    del transaction_cont
    del progress_cont

    # Save and close DataSources
    if not layer:
        outDataSource = None


def pg_layer(table, raster, srs, geom_type=ogr.wkbPolygon, server="localhost", dbname="eba", user="eba",
             password="ebaeba18", boudingBox=None):
    conn_str = "PG: host=%s dbname=%s user=%s password=%s" % (server, dbname, user, password)

    logging.info("Trying to connect PostgresSQL database: {}".format(conn_str))
    conn = ogr.Open(conn_str)
    assert conn

    if boudingBox:
        logging.info("Loading boundig box: {}".format(boudingBox))
        bblayer = conn.GetLayer(boudingBox)
        bbfeature = bblayer.GetNextFeature()

        logging.info("Getting the first Geometry")
        boudingBox = bbfeature.GetGeometryRef()

        assert boudingBox

    gdal_options = ['OVERWRITE=YES']

    logging.info("Trying to create table: {}, {}, {}".format(table, str(geom_type), str(gdal_options)))
    logging.info("With projection: {}".format(str(srs)))
    layer = conn.CreateLayer(table, srs, geom_type, gdal_options)

    ext = extent(raster)

    logging.info("Creating a boundig box with extent: {}".format(str(ext)))
    grid(table, ext["xmin"], ext["xmax"], ext["ymin"], ext["ymax"], ext["height"], ext["width"], layer, boudingBox)

    del conn


if __name__ == "__main__":
    #
    # example run : $ python grid.py <full-path><output-shapefile-name>.shp xmin xmax ymin ymax gridHeight gridWidth
    # python grid.py grid.shp 992325.66 1484723.41 494849.32 781786.14 10000 10000
    #
    parser = argparse.ArgumentParser(description="OGR FISH GRID")
    parser.add_argument("-s", "--server", type=str, default="localhost")
    parser.add_argument("-d", "--dbname", type=str, default="eba")
    parser.add_argument("-u", "--user", type=str, default="eba")
    parser.add_argument("-p", "--password", type=str, default="ebaeba18")
    parser.add_argument("-e", "--epsg", type=int, default=5880)
    parser.add_argument("-l", "--log", type=str, default=None, help="Logs to a file. Default 'console'.")
    parser.add_argument("-b", "--bb", type=str, default=None, help="Bounding Box table.")
    parser.add_argument("-t", "--table", type=str, required=True)
    parser.add_argument("-r", "--rasterpath", type=str, required=True, help="Raster file.")
    args = parser.parse_args()

    if args.log:
        logging.basicConfig(filename=args.log, level=logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler())
    else:
        logging.basicConfig(level=logging.INFO)

    try:
        logging.info("Running 'FISH GRID' to path '{}'...".format(args.table))
        ti = time.clock()

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(args.epsg)

        pg_layer(args.table, args.rasterpath, srs, server=args.server, dbname=args.dbname, user=args.user,
                 password=args.password, boudingBox=args.bb)

        tf_sec = int((time.clock() - ti) % 60)
        tf_min = int((tf_sec / 60) % 60)
        tf_h = int((tf_min / 60) % 24)
        logging.info("Table created with success in {} hours {} minutes {} seconds!".format(tf_h, tf_min, tf_sec))
    except Exception as e:
        logging.error("Error to 'FISH GRID' file: {}".format(str(e)))
