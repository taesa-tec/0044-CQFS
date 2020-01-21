import logging

from os.path import basename
from datetime import datetime
from qgis.core import QgsFeatureRequest, QgsField, QgsSpatialIndex
from processing.tools import dataobjects
from PyQt4.QtCore import QVariant
from ..qt_handler import QtHandler


class Presence(object):

    logger = logging.getLogger('presence')
    pt_br_format = '%d/%m/%Y %H:%M'

    def __init__(self, grid_path, bbox_path, field='presence'):
        if not isinstance(field, str):
            error_msg = 'Field is not str, got "{}".'.format(str(field))
            self.logger.fatal(error_msg)
            raise RuntimeError(error_msg)

        self.grid = dataobjects.getObjectFromUri(grid_path)
        if not self.grid:
            error_msg = u'Fail to create QgsGeometry of grid "{}".'.format(unicode(grid_path))
            self.logger.fatal(error_msg)
            raise RuntimeError(error_msg)

        self.bbox = dataobjects.getObjectFromUri(bbox_path)
        if not self.bbox:
            error_msg = u'Fail to create QgsGeometry of bbox "{}".'.format(unicode(bbox_path))
            self.logger.fatal(error_msg)
            raise RuntimeError(error_msg)

        self.field_name = field
        self.field_to_check_null = field
        self.basename_vector = basename(unicode(bbox_path))
        self.grid_index = self.__sp_index_factory(self.grid)
        self.bbox_index = self.__sp_index_factory(self.bbox)

        self.__init_fields()

    def __init_fields(self):
        self.grid.startEditing()
        self.__remove_create_field(self.field_name)
        self.grid.commitChanges()

    def fill_cell(self):
        last_progress = 0
        total = 100.0 / self.bbox.featureCount() if self.bbox.featureCount() > 0 else 1
        dlg, bar = QtHandler.progress_dialog(label=u'Fill grid with {}...'.format(self.basename_vector))

        start_time = datetime.now()
        str_start_time = start_time.strftime(self.pt_br_format)
        self.logger.info('Running presence to "{}" at {}...'.format(self.basename_vector, str_start_time))

        null = unicode('NULL')
        self.grid.startEditing()

        for current, ft in enumerate(self.grid.getFeatures()):
            if unicode(ft[self.field_to_check_null]) != null:
                continue

            ids = self.bbox_index.intersects(ft.geometry().boundingBox())
            if ids is not None and len(ids) > 0:
                self.__set_feature(ft)
                self.grid.updateFeature(ft)

            progress = int(current * total)
            if progress != last_progress and progress % 10 == 0:
                self.logger.debug('{}%'.format(str(progress)))
                bar.setValue(progress)
            last_progress = progress

        if last_progress != 100:
            bar.setValue(100)

        self.grid.commitChanges()

        self.logger.info('Fill cell without intersection...')
        self.__fill_cell_without_intersection()

        end_time = datetime.now()
        time_elapsed = end_time - start_time

        str_end_time = end_time.strftime(self.pt_br_format)
        self.logger.info('Summing up, done at {}! Time elapsed {}(hh:mm:ss.ms)'.format(str_end_time, time_elapsed))

        bar.close()
        dlg.close()

    def __fill_cell_without_intersection(self):
        request = self.__null_feature_request(self.field_to_check_null)

        value = 0.0
        self.grid.startEditing()
        for ft in self.grid.getFeatures(request):
            self.__set_feature(ft, value)
            self.grid.updateFeature(ft)
        self.grid.commitChanges()

    def __set_feature(self, ft_grid, value=1.0):
        ft_grid[self.field_name] = value

    def __remove_create_field(self, field_name, field_len=24, field_prec=15, field_type='number'):
        idx = self.grid.fieldNameIndex(field_name)
        writer = self.grid.dataProvider()

        if idx != -1:
            writer.deleteAttributes([idx])
            self.grid.updateFields()

        fn = field_name[:10]
        if field_type == 'number':
            field = QgsField(fn, QVariant.Double, '', field_len, field_prec)
        elif field_type == 'string':
            field = QgsField(fn, QVariant.String)
        else:
            raise RuntimeError('Olny number and string area defined.')

        writer.addAttributes([field])
        self.grid.updateFields()

    @staticmethod
    def __sp_index_factory(layer):
        index = QgsSpatialIndex()
        for ft in layer.getFeatures():
            index.insertFeature(ft)
        return index

    @staticmethod
    def __null_feature_request(field_to_check_null, fid=None):
        if fid is None:
            request = QgsFeatureRequest()
        else:
            request = QgsFeatureRequest(fid)

        request.setFilterExpression(Presence.__null_feature_expression(field_to_check_null))
        return request

    @staticmethod
    def __null_feature_expression(field_to_check_null):
        return '"%s" is NULL' % field_to_check_null


if __name__ == '__main__' or __name__ == '__console__':
    logging.basicConfig(level=logging.DEBUG)

    logging.info('Starts populate grid...')
    start_time = datetime.now()

    cs = Presence(
        r'D:\Projetos\0023.2016_TAESA\data\iginicao\tmp\grid.shp',
        r'D:\Projetos\0023.2016_TAESA\data\iginicao\pontos_queimada.shp',
        'QUEIMADA'
    )

    cs.fill_cell()

    end_time = datetime.now()
    time_elapsed = end_time - start_time

    pt_br_format = '%d/%m/%Y %H:%M'
    str_end_time = end_time.strftime(pt_br_format)
    logging.info('Summing up, done at {}! Time elapsed {}(hh:mm:ss.ms)'.format(str_end_time, time_elapsed))
