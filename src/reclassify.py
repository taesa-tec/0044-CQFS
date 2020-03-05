import logging
import os

from time import time

import numpy as np
from osgeo import gdal


class Reclassify(object):
    def __init__(self, reclass, format='GTiff', bands=1):
        assert reclass.input_raster
        assert reclass.output_raster
        assert os.path.isfile(reclass.input_raster)

        self.__logger = logging.getLogger('reclassify')
        self.__logger.info(u'Loading the reference raster: {}'.format(unicode(reclass.input_raster)))
        ds = gdal.Open(reclass.input_raster, gdal.gdalconst.GA_ReadOnly)
        assert ds

        ds_bands = ds.RasterCount
        if bands > ds_bands:
            raise RuntimeError('Number of bands is greater than raster count.')

        self.__base_raster = ds
        self.__format = format
        self.__bands = bands
        self.__impl = reclass

    def apply(self):
        raster = self.new_raster_from_base(self.__impl.output_raster)
        cols = self.__base_raster.RasterXSize
        rows = self.__base_raster.RasterYSize
        self.__logger.info('Cloning raster with ({}) rows and ({}) columns'.format(rows, cols))

        ti = time()
        for i in range(self.__bands):
            band = i + 1

            base_band = self.__base_raster.GetRasterBand(band)
            base_array = np.array(base_band.ReadAsArray())
            nodata = base_band.GetNoDataValue()

            new_band = raster.GetRasterBand(band)
            new_band.WriteArray(self.__impl.apply(base_array, nodata))
            new_band.FlushCache()
        del raster
        self.__logger.info(u'Raster "{}" created with success in {} seconds!'.format(unicode(self.__impl.output_raster), str(time() - ti)))

    def new_raster_from_base(self, output):
        cols = self.__base_raster.RasterXSize
        rows = self.__base_raster.RasterYSize
        self.__logger.info(u'Creating new raster with ({}) rows and ({}) columns'.format(rows, cols))

        projection = self.__base_raster.GetProjection()
        geotransform = self.__base_raster.GetGeoTransform()

        driver = gdal.GetDriverByName(self.__format)

        new_raster = driver.Create(output, cols, rows, self.__bands, self.__impl.datatype)
        new_raster.SetProjection(projection)
        new_raster.SetGeoTransform(geotransform)

        for i in range(self.__bands):
            n = i + 1
            band = new_raster.GetRasterBand(n)
            nodata_value = self.__impl.nodata or self.__base_raster.GetRasterBand(n).GetNoDataValue()
            band.SetNoDataValue(nodata_value)
            band.Fill(nodata_value)
            band.FlushCache()
        return new_raster


