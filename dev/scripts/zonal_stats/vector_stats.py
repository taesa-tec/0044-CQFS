"""
https://gis.stackexchange.com/questions/224930/how-to-select-polygons-which-contain-at-least-one-point-with-spatial-index/224954?noredirect=1#comment347399_224954
https://gis.stackexchange.com/questions/168697/performing-a-spatial-query-in-a-loop-in-pyqgis
https://gis.stackexchange.com/questions/270575/how-to-get-feature-id-by-using-qgsexpression
https://gis.stackexchange.com/questions/54057/how-to-read-the-attribute-values-using-pyqgis/138027
https://gis.stackexchange.com/questions/109078/how-to-delete-column-field-in-pyqgis
"""
from datetime import datetime
from PyQt4.QtCore import QVariant

# test
from qgis.core import *
from qgis.gui import QgsMapCanvas
from PyQt4.QtGui import *
from CQFS.dev.scripts.grid.qgis_interface import QgisInterface
from processing.tools import dataobjects, vector
# end


class CellularSpace(object):

    def __init__(self, grid_path, bbox_path, field_to_check_null, fields):
        assert field_to_check_null is not None
        assert fields is not None and isinstance(fields, dict)

        self.grid = dataobjects.getObjectFromUri(grid_path)
        self.bbox = dataobjects.getObjectFromUri(bbox_path)

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
                        field_name = template.format(str(int(value)))
                        self.__remove_create_field(field_name)
                        self.subfields[name]['names'].append(field_name)
            self.grid.commitChanges()

    def fill_cell(self):
        # progress bar
        progress_cont = 0.0
        progress_previous = 0.0
        progress_total = float(self.bbox.featureCount())
        length = 50
        fill = '#'

        for ft_bbox in self.bbox.getFeatures():
            if ft_bbox.id() == 2925:
                bbox_geom = ft_bbox.geometry()
                grid_ids = self.grid_index.intersects(bbox_geom.boundingBox())

                if grid_ids is None or len(grid_ids) == 0:
                    progress_cont += 1
                    continue

                border_features, border_current_area = self.__fill_cell_within_bbox(ft_bbox, grid_ids)

                if len(border_features) > 0:
                    self.__fill_cell_in_border_bbox(ft_bbox, border_current_area, border_features)

            # progress bar
            progress_cont += 1
            progress = 100 * (progress_cont / progress_total)
            if round(progress, 1) != round(progress_previous, 1):
                percent = ('{0:.' + str(1) + 'f}').format(progress)
                filled_length = int(length * progress_cont // progress_total)
                bar = fill * filled_length + '-' * (length - filled_length)
                out = '%s |%s| %s%% %s' % ('Progress:', bar, percent, 'Complete')
                print(out)

            progress_previous = progress

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

            class_name = template.format(str(int(bbox_attr)))
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
    """
    <init/>
    """
    app = QApplication([])
    QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 2.18\apps\qgis', True)
    QgsApplication.initQgis()

    canvas = QgsMapCanvas()
    iface = QgisInterface(canvas)
    """
    </init>
    """

    """
    main
    """
    print('Starts populate grid...')
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
    print('Summing up, done at {}! Time elapsed {}(hh:mm:ss.ms)'.format(str_end_time, time_elapsed))
    """
    <end/>
    """
    QgsApplication.exitQgis()
    app.exit()
    """
    </end>
    """
