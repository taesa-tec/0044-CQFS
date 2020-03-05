# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-09-06
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Geoambiente
        email                : gisti@geoambiente.com.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import logging
import os.path

# Always initialize qgis first. Module qgis set PyQt settings.
from qgis.core import QgsMapLayer
from qgis.gui import QgsMessageBar

# Initialize Qt
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources

# CQFS
from cqfs_dialog import CQFSDialog
from src.cqfs_config import setup_logger
from src.layer_util import define_crs_if_not_exist, layers_name_by_type, is_layer_line_or_multiline, is_layer_point_or_multipoint, is_layer_polygon
from src.criticidade import Criticidade
from src.layer_util import define_crs_if_not_exist, layers_name_by_type, is_layer_line_or_multiline, \
    is_layer_point_or_multipoint

from src.propagacao import Propagacao
from src.ignicao import Ignicao
from src.vulnerabilidade import Vulnerabilidade
from src.handler.tab_handler import TabHandler
from src.risco_fogo import RiscoFogo


resources.remove_imports_errors()
setup_logger(__file__)


class CQFS:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CQFS_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&CQFS')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'CQFS')
        self.toolbar.setObjectName(u'CQFS')

        self.__logger = logging.getLogger('cqfs')
        self.__logger.info('Create an instance of CQFS.')
        self.propagacao = None
        self.ignicao = None
        self.vulnerabilidade = None
        self.risco_fogo = None
        self.criticidade = None

        define_crs_if_not_exist()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CQFS', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = CQFSDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/CQFS/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Criticidade à Queimadas em Faixas de Servidão'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.dlg.line_saida_modelo.clear()
        self.dlg.btn_saida_modelo.clicked.connect(lambda: self.select_output_file(self.dlg.line_saida_modelo))
        self.dlg.ignicao_btn_saida_modelo.clicked.connect(lambda: self.select_output_file(self.dlg.ignicao_line_saida_modelo, '*.shp'))
        self.dlg.btn_saida_vulnerabilidade.clicked.connect(lambda: self.select_output_file(self.dlg.line_saida_vulnerabilidade, '*.shp'))
        self.dlg.btn_saida_risco_tecnico.clicked.connect(lambda: self.select_output_file(self.dlg.line_saida_risco_tecnico, '*.tiff'))
        self.dlg.btn_saida_criticidade.clicked.connect(lambda: self.select_output_file(self.dlg.line_saida_criticidade, '*.shp'))

        self.dlg.ignicao_btn_entrada_formula.clicked.connect(lambda: self.select_input_file(self.dlg.ignicao_line_entrada_formula, '*.yaml'))

        self.destroy_propagacao()
        self.destroy_ignicao()
        self.destroy_vulnerabilidade()
        self.destroy_criticidade()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.destroy_propagacao()
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&CQFS'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()

        layers, rasters_name, lines_name, polygons_name, points_name = self.interface_layers()

        self.init_propagacao(rasters_name, lines_name)
        self.init_ignicao(rasters_name, lines_name, polygons_name, points_name)
        self.init_vulnerabilidade()
        self.init_risco_fogo()
        self.init_criticidade(rasters_name)

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            handler = TabHandler()
            handler.handle(cqfs=self, layers=layers, rasters_name=rasters_name, lines_name=lines_name, polygons_name=polygons_name, points_name=points_name)

    def interface_layers(self):
        layers = self.iface.legendInterface().layers()
        base_layer_name = 'Selecione o layer...'

        lines_name = layers_name_by_type(layers, QgsMapLayer.VectorLayer, __sof_=is_layer_line_or_multiline)
        lines_name.insert(0, base_layer_name)
        
        polygons_name = layers_name_by_type(layers, QgsMapLayer.VectorLayer, __sof_=is_layer_polygon)
        polygons_name.insert(0, base_layer_name)

        points_name = layers_name_by_type(layers, QgsMapLayer.VectorLayer, __sof_=is_layer_point_or_multipoint)
        points_name.insert(0, base_layer_name)

        rasters_name = layers_name_by_type(layers, QgsMapLayer.RasterLayer)
        self.__logger.info(u'Rasters {}...'.format(u', '.join(rasters_name)))
        rasters_name.insert(0, base_layer_name)

        return layers, rasters_name, lines_name, polygons_name, points_name

    def init_propagacao(self, rasters_name, vectors_name):
        self.__logger.info('Init propagacao...')

        self.destroy_propagacao()

        self.propagacao = Propagacao(
            vectors_name,
            rasters_name,
            self.dlg.combo_linha_transmissao,
            self.dlg.combo_vegetacao,
            self.dlg.combo_clinografia,
            self.dlg.combo_orientacao_vertente,
            self.dlg.combo_proximidade_estradas,
            self.dlg.combo_hipsometria
        )

    def init_ignicao(self, rasters_name, lines_name, polygons_name, points_name):
        self.__logger.info('Init propagacao...')
        self.destroy_ignicao()
        self.ignicao = Ignicao(self.dlg, rasters_name, lines_name, polygons_name, points_name)

    def init_vulnerabilidade(self):
        self.__logger.info('Init Vulnerabilidade...')

        self.destroy_vulnerabilidade()

        layers = self.iface.legendInterface().layers()
        base_layer_name = 'Selecione o layer...'

        vectors_vao_name = layers_name_by_type(layers, QgsMapLayer.VectorLayer, __sof_=is_layer_polygon)
        vectors_vao_name.insert(0, base_layer_name)

        vectors_pc_name = layers_name_by_type(layers, QgsMapLayer.VectorLayer, __sof_=is_layer_point_or_multipoint)
        vectors_pc_name.insert(0, base_layer_name)

        self.vulnerabilidade = Vulnerabilidade(
            vectors_vao_name,
            vectors_pc_name,
            self.dlg.combo_vao,
            self.dlg.combo_ponto_critico,
            self.dlg.combo_torres
        )

    def init_risco_fogo(self):
        self.__logger.info('Init Risco Fogo...')
        self.destroy_risco_fogo()

        layers = self.iface.legendInterface().layers()
        base_layer_name = 'Selecione o layer...'

        vectors_name = layers_name_by_type(layers, QgsMapLayer.VectorLayer, __sof_=is_layer_polygon)
        vectors_name.insert(0, base_layer_name)

        rasters_name = layers_name_by_type(layers, QgsMapLayer.RasterLayer)
        self.__logger.info(u'Rasters {}...'.format(', '.join(rasters_name)))
        rasters_name.insert(0, base_layer_name)

        self.risco_fogo = RiscoFogo(self.dlg, vectors_name, rasters_name)

    def init_criticidade(self, rasters_name):
        self.__logger.info('Init Criticidade...')

        self.destroy_criticidade()

        layers = self.iface.legendInterface().layers()
        base_layer_name = 'Selecione o layer...'

        vectors_name = layers_name_by_type(layers, QgsMapLayer.VectorLayer, __sof_=is_layer_polygon)
        vectors_name.insert(0, base_layer_name)

        self.criticidade = Criticidade(
            rasters_name,
            vectors_name,
            self.dlg.combo_vulnerabilidade,
            self.dlg.combo_risco_fogo
        )

    def select_output_file(self, lineEdit, extension='*.tif'):
        filename = QFileDialog.getSaveFileName(self.dlg, "Selecione o arquivo de saída ", "", extension)
        lineEdit.setText(filename)
        self.__logger.info(u'Output model: "{}".'.format(unicode(filename)))

    def select_input_file(self, lineEdit, extension='*.yaml'):
        filename = QFileDialog.getOpenFileName(self.dlg, "Selecione o arquivo de entrada ", "", extension)
        lineEdit.setText(filename)
        self.__logger.info(u'Input model: "{}".'.format(unicode(filename)))

    def destroy_propagacao(self):
        if self.propagacao is not None:
            self.propagacao.destroy()
            self.propagacao = None

    def destroy_ignicao(self):
        if self.ignicao is not None:
            self.ignicao.destroy()
            self.ignicao = None

    def destroy_vulnerabilidade(self):
        if self.vulnerabilidade is not None:
            self.vulnerabilidade.destroy()
            self.vulnerabilidade = None

    def destroy_risco_fogo(self):
        if self.risco_fogo is not None:
            self.risco_fogo.destroy()
            self.risco_fogo = None

    def destroy_criticidade(self):
        if self.criticidade is not None:
            self.criticidade.destroy()
            self.criticidade = None

    def show_error(self, msg):
        self.show_message(msg, QgsMessageBar.CRITICAL)

    def show_warn(self, msg):
        self.show_message(msg, QgsMessageBar.WARNING)

    def show_info(self, msg):
        self.show_message(msg, QgsMessageBar.INFO)

    def show_message(self, msg, level, duration=10):
        self.iface.messageBar().pushMessage(msg, level=level, duration=duration)
