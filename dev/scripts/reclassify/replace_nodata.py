import datetime

import gdal, ogr, osr, os
import numpy as np


def raster2array(rasterfn):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    return np.array(band.ReadAsArray())


def getNoDataValue(rasterfn):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    return band.GetNoDataValue()


def array2raster(rasterfn, newRasterfn, nodata, array):
    raster = gdal.Open(rasterfn)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = raster.RasterXSize
    rows = raster.RasterYSize
    inband = raster.GetRasterBand(1)
    datatype = inband.DataType

    driver = gdal.GetDriverByName('GTiff')

    outRaster = driver.Create(newRasterfn, cols, rows, 1, datatype)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(raster.GetProjectionRef())
    outRaster.SetProjection(outRasterSRS.ExportToWkt())

    outband = outRaster.GetRasterBand(1)
    outband.SetNoDataValue(nodata)
    outband.WriteArray(array)
    outband.FlushCache()


if __name__ == '__main__':
    date_formatter = '%Y%m%d%H%M%S'
    time = datetime.datetime.now().strftime(date_formatter)

    rasterfn = r'D:\Projetos\0023.2016_TAESA\data\propagacao\uso_solo.tif'
    newRasterfn = r'C:\Users\heitor.carneiro\.qgis2\python\plugins\CQFS\impl\data\output\output_{}.tif'.format(str(time))
    newValue = -9999

    # Convert Raster to array
    rasterArray = raster2array(rasterfn)

    # Get no data value of array
    # noDataValue = getNoDataValue(rasterfn)

    # Updata no data value in array with new value
    rasterArray[rasterArray == 250] = newValue

    # Write updated array to new raster
    array2raster(rasterfn, newRasterfn, newValue, rasterArray)
