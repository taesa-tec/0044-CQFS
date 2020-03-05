# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-09-20
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

from PyQt4.QtGui import QProgressDialog, QProgressBar

__logger = logging.getLogger('qt_util')


class QtHandler(object):

    logger = logging.getLogger('qt_util')

    log_message_on_change = u'Metodo "{}" de indice "{}" com valor "{}" [{}].'
    log_error_on_change = u'Falha ao executar evento para combobox "{}", indice {} e texto "{}": {}'

    def __init__(self):
        self.__combo_enabled = {}
        self.__combo_name_by_qt_object = {}
        self.__combo_name_by_layer_index = {}
        self.__layers_name_as_str = ''

    @property
    def combo_name_by_layer_index(self):
        return self.__combo_name_by_layer_index

    def init_combobox(self, layers_name, **kwargs):
        for name in layers_name:
            self.__combo_enabled[name] = True

        for name, combo in kwargs.iteritems():
            self.__combo_name_by_qt_object[name] = combo
            self.__combo_name_by_layer_index[name] = 0

        self.__layers_name_as_str = ','.join(self.__combo_name_by_qt_object.keys())

    def clear_combobox(self):
        for name in self.__combo_enabled.keys():
            del self.__combo_enabled[name]

        for name in self.__combo_name_by_qt_object.keys():
            combo_qt = self.__combo_name_by_qt_object[name]
            QtHandler.disconnect(combo_qt.currentIndexChanged)

            del self.__combo_name_by_qt_object[name]
            del self.__combo_name_by_layer_index[name]

        self.__layers_name_as_str = ''

    def on_combobox_change(self, combo_name, combo_qt, index):
        """
        Base event to unselected option.

        :param combo_name: A string with combo_name.
        :param combo_qt: The qt object.
        :param index: An int with index of layer.
        :return: void
        """
        text = combo_qt.itemText(index)
        if len(self.__combo_enabled) == 0 or unicode(text) == u'':
            return

        try:
            if self.__combo_name_by_layer_index[combo_name]:
                old_index = self.__combo_name_by_layer_index[combo_name]
                old_text = combo_qt.itemText(old_index)
                self.__combo_enabled[old_text] = not self.__combo_enabled[old_text]
                self.__disable_rasters_selected(combo_name, old_index, old_text)

            if index == 0:
                self.__combo_name_by_layer_index[combo_name] = None
                self.logger.info('Reset "{}".'.format(combo_name))
            else:
                self.__combo_enabled[text] = not self.__combo_enabled[text]
                self.__disable_rasters_selected(combo_name, index, text)
                self.__combo_name_by_layer_index[combo_name] = index

                self.logger.info(self.log_message_on_change.format(combo_name, str(index), text, self.__layers_name_as_str))
        except Exception as e:
            self.logger.fatal(self.log_error_on_change.format(combo_name, str(index), text, str(e)))

    def __disable_rasters_selected(self, combo_name, index, text):
        enabled = self.__combo_enabled[text]
        for n, c in self.__combo_name_by_qt_object.iteritems():
            if n != combo_name:
                c.model().item(index).setEnabled(enabled)

    @staticmethod
    def set_combobox(combo, layers_name, __sof__):
        """
        Apply an event to a combobox.

        :param combo: PyQt Combobox
        :param layers_name: list of layers name
        :param __sof__: second order function
        :return: void
        """
        combo.clear()
        combo.addItems(list(layers_name))
        on_change = lambda index: __sof__(combo, index)
        QtHandler.reconnect(combo.currentIndexChanged, newhandler=on_change)

    @staticmethod
    def set_radio(radio, __sof__):
        """
        Apply an event to a radio button.

        :param radio: PyQt Radio Button
        :param __sof__: second order function
        :return: void
        """
        QtHandler.reconnect(radio.toggled, newhandler=__sof__)

    @staticmethod
    def disconnect(signal, oldhandler=None):
        """
        https://gis.stackexchange.com/questions/137160/odd-behavior-in-a-qgis-plugin-my-function-is-triggered-twice
        https://stackoverflow.com/questions/21586643/pyqt-widget-connect-and-disconnect

        :param signal: PyQt object
        :param oldhandler: function
        :return: void
        """
        while True:
            try:
                if oldhandler is not None:
                    signal.disconnect(oldhandler)
                else:
                    signal.disconnect()
            except TypeError:
                break

    @staticmethod
    def reconnect(signal, newhandler=None, oldhandler=None):
        """
        https://gis.stackexchange.com/questions/137160/odd-behavior-in-a-qgis-plugin-my-function-is-triggered-twice
        https://stackoverflow.com/questions/21586643/pyqt-widget-connect-and-disconnect

        :param signal: PyQt object
        :param newhandler: function
        :param oldhandler: function
        :return: void
        """
        QtHandler.disconnect(signal, oldhandler)
        if newhandler is not None:
            signal.connect(newhandler)

    @staticmethod
    def progress_dialog(progress=0, title='CQFS Progress', label='Running...'):
        dialog = QProgressDialog()
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setAutoClose(True)

        bar = QProgressBar(dialog)
        bar.setTextVisible(True)
        bar.setValue(progress)
        bar.setMaximum(100)

        dialog.setBar(bar)
        dialog.setMinimumWidth(300)
        dialog.show()

        if int(progress) == 0:
            bar.setValue(0)
        return dialog, bar
