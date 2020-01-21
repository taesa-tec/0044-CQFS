import numpy
import logging

try:
    from scipy.stats.mstats import mode
    has_SciPy = True
except:
    has_SciPy = False

from os.path import basename
from datetime import datetime
from osgeo import gdal, ogr, osr
from qgis.core import QgsRectangle, QgsGeometry, QgsFeature

from processing.tools.vector import VectorWriter
from processing.tools.raster import mapToPixel
from processing.tools import dataobjects, vector

from ..qt_handler import QtHandler


class ZonalStatisticsNewLayer(object):

    valid_operations = ('min', 'max', 'sum', 'count', 'mean', 'std', 'unique', 'range', 'var', 'median', 'mode')
    logger = logging.getLogger('zonal_stats')
    pt_br_format = '%d/%m/%Y %H:%M'

    def __init__(self, source_vector, source_raster, destination, band_number=1, column_prefix='', use_global_extent=False, operations=('mean',), fields_alias=None):
        self.layer = dataobjects.getObjectFromUri(source_vector)

        if not self.layer:
            raise RuntimeError('Vector "{}" not found.'.format(source_vector))

        self.raster_ds = gdal.Open(source_raster, gdal.GA_ReadOnly)

        if not self.raster_ds:
            raise RuntimeError('Raster "{}" not found.'.format(source_raster))

        self.source_raster = source_raster
        self.basename_raster = basename(self.source_raster)
        self.band_number = band_number
        self.column_prefix = column_prefix
        self.use_global_extent = use_global_extent

        self.raster_band = self.raster_ds.GetRasterBand(band_number)

        self.no_data = self.raster_band.GetNoDataValue()
        self.scale = self.raster_band.GetScale()
        self.offset = self.raster_band.GetOffset()

        if self.scale is None:
            self.scale = 1.0

        if self.offset is None:
            self.offset = 0.0

        self.fields = self.layer.pendingFields()
        self.destination = destination

        self.operations = operations
        self.operations_idx = {}

        if fields_alias is None:
            fields_alias = operations

        if len(fields_alias) != len(operations):
            raise RuntimeError('Invalid alias fields.')

        alias = {}
        for i, al in enumerate(fields_alias):
            op = operations[i]
            alias[op] = al

        self.alias = alias

    def perform(self):
        geo_transform = self.raster_ds.GetGeoTransform()

        raster_b_box = self.__get_raster_b_box(geo_transform)
        raster_geom = QgsGeometry.fromRect(raster_b_box)
        crs = self.__create_spatial_reference()

        if self.use_global_extent:
            src_offset, src_array, new_geo_transform = self.__get_global_extent(raster_b_box, geo_transform)
        else:
            src_offset = None
            src_array = None
            new_geo_transform = None

        mem_vector_driver = ogr.GetDriverByName('Memory')
        mem_raster_driver = gdal.GetDriverByName('MEM')

        self.__populate_fields_operations()
        writer = VectorWriter(self.destination, None, self.fields.toList(), self.layer.wkbType(), self.layer.crs(), None)

        out_feat = QgsFeature()
        out_feat.initAttributes(len(self.fields))
        out_feat.setFields(self.fields)

        features = vector.features(self.layer)
        last_progress = 0
        total = 100.0 / len(features) if len(features) > 0 else 1

        dlg, bar = QtHandler.progress_dialog(label='Fill grid with {}...'.format(self.basename_raster))

        start_time = datetime.now()
        str_start_time = start_time.strftime(self.pt_br_format)
        self.logger.info('Running zonal stats to "{}" at {}...'.format(self.basename_raster, str_start_time))

        for current, f in enumerate(features):
            geom = f.geometry()

            intersected_geom = raster_geom.intersection(geom)
            ogr_geom = ogr.CreateGeometryFromWkt(intersected_geom.exportToWkt())

            if not self.use_global_extent:
                bbox = intersected_geom.boundingBox()

                x_min = bbox.xMinimum()
                x_max = bbox.xMaximum()
                y_min = bbox.yMinimum()
                y_max = bbox.yMaximum()

                (startColumn, startRow) = mapToPixel(x_min, y_max, geo_transform)
                (endColumn, endRow) = mapToPixel(x_max, y_min, geo_transform)

                width = endColumn - startColumn
                height = endRow - startRow

                if width == 0 or height == 0:
                    continue

                src_offset = (startColumn, startRow, width, height)
                src_array = self.raster_band.ReadAsArray(*src_offset)
                src_array = src_array * self.scale + self.offset

                new_geo_transform = (
                    geo_transform[0] + src_offset[0] * geo_transform[1],
                    geo_transform[1],
                    0.0,
                    geo_transform[3] + src_offset[1] * geo_transform[5],
                    0.0,
                    geo_transform[5],
                )

            # Create a temporary vector layer in memory
            mem_vds = mem_vector_driver.CreateDataSource('out')
            mem_layer = mem_vds.CreateLayer('poly', crs, ogr.wkbPolygon)

            ft = ogr.Feature(mem_layer.GetLayerDefn())
            ft.SetGeometry(ogr_geom)
            mem_layer.CreateFeature(ft)
            ft.Destroy()

            # Rasterize it
            rasterized_ds = mem_raster_driver.Create('', src_offset[2], src_offset[3], 1, gdal.GDT_Byte)
            rasterized_ds.SetGeoTransform(new_geo_transform)
            gdal.RasterizeLayer(rasterized_ds, [1], mem_layer, burn_values=[1])
            rasterized_array = rasterized_ds.ReadAsArray()

            out_feat.setGeometry(geom)
            masked = numpy.ma.MaskedArray(src_array, mask=numpy.logical_or(src_array == self.no_data, numpy.logical_not(rasterized_array)))

            attrs = self.__zonal_stats(f, masked)
            out_feat.setAttributes(attrs)
            writer.addFeature(out_feat)

            del mem_vds
            del rasterized_ds

            progress = int(current * total)
            if progress != last_progress and progress % 10 == 0:
                self.logger.debug('{}%'.format(str(progress)))
                bar.setValue(progress)
            last_progress = progress

        if last_progress != 100:
            bar.setValue(100)

        bar.close()
        dlg.close()
        del dlg

        del writer
        del self.raster_ds

        end_time = datetime.now()
        time_elapsed = end_time - start_time

        str_end_time = end_time.strftime(self.pt_br_format)
        self.logger.info('Summing up, done at {}! Time elapsed {}(hh:mm:ss.ms)'.format(str_end_time, time_elapsed))

    def __zonal_stats(self, f, masked):
        attrs = f.attributes()

        for op, idx in self.operations_idx.iteritems():
            if op == 'min':
                v = float(masked.min())
            elif op == 'max':
                v = float(masked.max())
            elif op == 'sum':
                v = float(masked.sum())
            elif op == 'count':
                v = int(masked.count())
            elif op == 'mean':
                v = float(masked.mean())
            elif op == 'std':
                v = float(masked.std())
            elif op == 'unique':
                v = numpy.unique(masked.compressed()).size
            elif op == 'range':
                v = float(masked.max()) - float(masked.min())
            elif op == 'var':
                v = float(masked.var())
            elif op == 'median':
                v = float(numpy.ma.median(masked))
            elif op == 'mode':
                v = float(mode(masked, axis=None)[0][0])
            else:
                self.logger.warning('Unrecognized operation "{}".'.format(op))
                continue

            attrs.insert(idx, None if numpy.isnan(v) else v)
        return attrs

    def __populate_fields_operations(self):
        if not has_SciPy:
            temp_list = list(self.valid_operations)
            temp_list.remove('mode')
            self.valid_operations = tuple(temp_list)

        for op in self.valid_operations:
            if op in self.operations:
                alias = self.alias[op]
                self.operations_idx[op] = self.__find_or_create_field(alias)

    def __get_global_extent(self, raster_b_box, geo_transform):
        x_min = raster_b_box.xMinimum()
        x_max = raster_b_box.xMaximum()
        y_min = raster_b_box.yMinimum()
        y_max = raster_b_box.yMaximum()

        (startColumn, startRow) = mapToPixel(x_min, y_max, geo_transform)
        (endColumn, endRow) = mapToPixel(x_max, y_min, geo_transform)

        width = endColumn - startColumn
        height = endRow - startRow

        src_offset = (startColumn, startRow, width, height)
        src_array = self.raster_band.ReadAsArray(*src_offset)
        src_array = src_array * self.scale + self.offset

        new_geo_transform = (
            geo_transform[0] + src_offset[0] * geo_transform[1],
            geo_transform[1],
            0.0,
            geo_transform[3] + src_offset[1] * geo_transform[5],
            0.0,
            geo_transform[5],
        )

        return src_offset, src_array, new_geo_transform

    def __find_or_create_field(self, field_name, field_len=21, field_precision=6):
        idx, fields = vector.findOrCreateField(self.layer, self.fields, self.column_prefix + field_name, field_len, field_precision)
        self.fields = fields
        return idx

    def __get_raster_b_box(self, geo_transform):
        cell_x_size = abs(geo_transform[1])
        cell_y_size = abs(geo_transform[5])

        raster_x_size = self.raster_ds.RasterXSize
        raster_y_size = self.raster_ds.RasterYSize

        raster_b_box = QgsRectangle(
            geo_transform[0],
            geo_transform[3] - cell_y_size * raster_y_size,
            geo_transform[0] + cell_x_size * raster_x_size,
            geo_transform[3]
        )

        return raster_b_box

    def __create_spatial_reference(self):
        crs = osr.SpatialReference()
        crs.ImportFromProj4(str(self.layer.crs().toProj4()))
        return crs


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    grid_grid = r'D:\Projetos\0023.2016_TAESA\data\iginicao\tmp\grid.shp'
    raster_source = r'D:\Projetos\0023.2016_TAESA\data\iginicao\DENSIDADE_Albers.tif'
    destination_source = r'D:\Projetos\0023.2016_TAESA\data\iginicao\tmp\grid_zonal_2.shp'

    zs = ZonalStatistics(grid_grid, raster_source, destination_source, fields_alias=('DENS_MED',))
    zs.perform()
