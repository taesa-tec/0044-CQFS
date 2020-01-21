import logging

from os.path import basename
from datetime import datetime
from qgis.core import QgsFeatureRequest, QgsField, QgsSpatialIndex
from processing.tools import dataobjects
from PyQt4.QtCore import QVariant
from ..qt_handler import QtHandler


class CellularSpace(object):

    logger = logging.getLogger('cellular_space')
    pt_br_format = '%d/%m/%Y %H:%M'

    def __init__(self, grid_path, bbox_path, field_to_check_null, fields):
        if not isinstance(fields, dict):
            error_msg = 'Fields is not dict, got "{}".'.format(str(fields))
            self.logger.fatal(error_msg)
            raise RuntimeError(error_msg)

        if field_to_check_null not in fields:
            error_msg = 'Field "{}" used to check incomplete fill not found in fields argument.'.format(str(field_to_check_null))
            self.logger.fatal(error_msg)
            raise RuntimeError(error_msg)

        self.grid = dataobjects.getObjectFromUri(grid_path)
        if not self.grid:
            error_msg = 'Fail to create QgsGeometry of grid "{}".'.format(str(grid_path))
            self.logger.fatal(error_msg)
            raise RuntimeError(error_msg)

        self.bbox = dataobjects.getObjectFromUri(bbox_path)
        if not self.bbox:
            error_msg = 'Fail to create QgsGeometry of bbox "{}".'.format(str(bbox_path))
            self.logger.fatal(error_msg)
            raise RuntimeError(error_msg)

        self.basename_vector = basename(bbox_path)

        self.field_alias = {}
        self.subfields = {}
        self.__init_fields(fields)

        self.field_to_check_null = field_to_check_null

        self.grid_index = self.__sp_index_factory(self.grid)
        self.bbox_index = self.__sp_index_factory(self.bbox)

    def __init_fields(self, fields):
        create_subcolumn = {}

        self.grid.startEditing()
        for name, prop in fields.iteritems():
            dtype = prop['type']
            alias = prop['alias']

            self.field_alias[name] = alias
            self.__remove_create_field(name, field_type=dtype)

            if 'subcolumn' in prop:
                template = prop['subcolumn']
                create_subcolumn[name] = template
        self.grid.commitChanges()

        if len(create_subcolumn) > 0:
            self.grid.startEditing()
            for name, template in create_subcolumn.iteritems():
                alias = self.field_alias[name]
                idx = self.bbox.fieldNameIndex(alias)

                unique_values = self.bbox.uniqueValues(idx)
                if unique_values is not None and len(unique_values) > 0:
                    self.subfields[name] = {'template': template, 'names': []}

                    for value in unique_values:
                        str_value = str(int(value)).rjust(2, '0')
                        field_name = template.format(str_value)
                        self.__remove_create_field(field_name)
                        self.subfields[name]['names'].append(field_name)
            self.grid.commitChanges()

    def fill_cell(self):
        last_progress = 0
        total = 100.0 / self.bbox.featureCount() if self.bbox.featureCount() > 0 else 1
        dlg, bar = QtHandler.progress_dialog(label='Fill grid with {}...'.format(self.basename_vector))

        start_time = datetime.now()
        str_start_time = start_time.strftime(self.pt_br_format)
        self.logger.info('Running cellular space to "{}" at {}...'.format(self.basename_vector, str_start_time))

        for current, ft_bbox in enumerate(self.bbox.getFeatures()):
            bbox_geom = ft_bbox.geometry()
            grid_ids = self.grid_index.intersects(bbox_geom.boundingBox())

            if grid_ids is not None and len(grid_ids) > 0:
                border_features, border_current_area = self.__fill_cell_within_bbox(ft_bbox, grid_ids)

                if len(border_features) > 0:
                    self.__fill_cell_in_border_bbox(ft_bbox, border_current_area, border_features)

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

        end_time = datetime.now()
        time_elapsed = end_time - start_time

        str_end_time = end_time.strftime(self.pt_br_format)
        self.logger.info('Summing up, done at {}! Time elapsed {}(hh:mm:ss.ms)'.format(str_end_time, time_elapsed))

    def __fill_cell_in_border_bbox(self, bbox_ft, bbox_area_by_cell, border_cells):
        self.grid.startEditing()

        for i, bft in enumerate(border_cells):
            bft_geometry = bft.geometry()
            bbox_ids = self.bbox_index.intersects(bft_geometry.boundingBox())

            if bbox_ft.id() in bbox_ids:
                bbox_ids.remove(bbox_ft.id())

            area = bbox_area_by_cell[i]
            ft_selected = bbox_ft
            for bbfid in bbox_ids:
                ft_border = next(self.bbox.getFeatures(QgsFeatureRequest(bbfid)))

                intersection_geom = ft_border.geometry().intersection(bft_geometry)
                intersection_area = intersection_geom.area()

                if area < intersection_area:
                    area = intersection_area
                    ft_selected = ft_border

            self.__set_feature(ft_selected, bft)
            self.grid.updateFeature(bft)

        self.grid.commitChanges()

    def __fill_cell_within_bbox(self, ft_bbox, fid_intersects, null='NULL'):
        null = unicode(null)
        border_features = []
        border_current_area_by_features = []

        bbox_geom = ft_bbox.geometry()

        self.grid.startEditing()
        for gfid in fid_intersects:
            ft_grid = next(self.grid.getFeatures(QgsFeatureRequest(gfid)))

            if unicode(ft_grid[self.field_to_check_null]) != null:
                continue

            if bbox_geom.contains(ft_grid.geometry()):
                self.__set_feature(ft_bbox, ft_grid)
                self.grid.updateFeature(ft_grid)
            else:
                self.__add_bbox_area(border_features, border_current_area_by_features, bbox_geom, ft_grid)
        self.grid.commitChanges()

        return border_features, border_current_area_by_features

    def __set_feature(self, ft_bbox, ft_grid):
        for name, alias in self.field_alias.iteritems():
            bbox_attr = ft_bbox[alias]
            ft_grid[name] = bbox_attr

            self.__set_subfield(ft_grid, name, bbox_attr)

    def __set_subfield(self, ft_grid, name, bbox_attr):
        if name in self.subfields:
            props = self.subfields[name]
            template = props['template']

            str_value = str(int(bbox_attr)).rjust(2, '0')
            class_name = template.format(str_value)
            for field_name in props['names']:
                has_value = 0
                if field_name == class_name:
                    has_value = 1
                ft_grid[field_name] = float(has_value)

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
    def __add_bbox_area(border_features, border_bbox_area, bbox_geom, grid_feature):
        intersection_geom = bbox_geom.intersection(grid_feature.geometry())
        intersection_area = intersection_geom.area()
        border_bbox_area.append(intersection_area)
        border_features.append(grid_feature)

    @staticmethod
    def __sp_index_factory(layer):
        index = QgsSpatialIndex()
        for ft in layer.getFeatures():
            index.insertFeature(ft)
        return index


if __name__ == '__main__' or __name__ == '__console__':
    logging.basicConfig(level=logging.DEBUG)

    logging.info('Starts populate grid...')
    start_time = datetime.now()

    property_map = {
        'COD_CLASSE': {
            'type': 'number',
            'alias': 'codigo',
            'subcolumn': 'USO_{}_P'
        },
        'CLASSE': {
            'type': 'string',
            'alias': 'Classe'
        }
    }

    cs = CellularSpace(
        r'D:\Projetos\0023.2016_TAESA\data\iginicao\tmp\grid.shp',
        r'D:\Projetos\0023.2016_TAESA\data\iginicao\Uso_solo_Albers_v2.shp',
        'CLASSE',
        property_map
    )

    cs.fill_cell()

    end_time = datetime.now()
    time_elapsed = end_time - start_time

    pt_br_format = '%d/%m/%Y %H:%M'
    str_end_time = end_time.strftime(pt_br_format)
    logging.info('Summing up, done at {}! Time elapsed {}(hh:mm:ss.ms)'.format(str_end_time, time_elapsed))
