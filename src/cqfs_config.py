# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-09-10
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
import os
import datetime
import logging
import tempfile
import yaml

from constants import CQFS_CONFIG

__date_today = str(datetime.date.today())
__date_formatter = '%Y-%m-%d %H:%M:%S'
__log_formatter = logging.Formatter('%(levelname)s: %(asctime)s - %(name)s - %(message)s (%(funcName)s():%(pathname)s:%(lineno)d)')
__log_level = logging.DEBUG

__logger = logging.getLogger('cqfs_config')

__propagacao_default = dict(
    distance=500,
    dissolve=True,
    segments=5
)


def setup_logger(filepath):
    script_dir = os.path.dirname(filepath)
    script_basename = os.path.splitext(os.path.basename(filepath))[0]

    log_dir = os.path.abspath(os.path.join(script_dir, 'log'))
    log_basename = script_basename + '-' + __date_today + '.log'

    fh = logging.FileHandler(os.path.join(log_dir, log_basename))
    fh.setFormatter(__log_formatter)
    fh.setLevel(__log_level)

    logging.basicConfig(level=__log_level)
    logging.getLogger().addHandler(fh)


def load_config():
    """
    https://stackoverflow.com/questions/1773805/how-can-i-parse-a-yaml-file-in-python
    :return: dict
    """
    data = None
    if os.path.isfile(CQFS_CONFIG):
        with open(CQFS_CONFIG, 'r') as stream:
            try:
                data = yaml.load(stream)
            except yaml.YAMLError as exc:
                __logger.fatal('Fail to load config file "{}": {}'.format(CQFS_CONFIG, str(exc)))

    data = data or {}
    __set_default_config(data, 'propagacao', __propagacao_default)
    return data


def __set_default_config(data, plugin_name, params_default):
    if plugin_name not in data:
        data[plugin_name] = {}

    for k, v in params_default.iteritems():
        if k not in data[plugin_name]:
            __logger.warn('Loading default config for plugin "{}", {} = {}.'.format(plugin_name, k, str(v)))
            data[plugin_name][k] = v


def tmp_filename_without_extension():
    """
    https://stackoverflow.com/questions/26541416/generate-temporary-file-names-without-creating-actual-file-in-python
    :return string
    """
    temp_name = next(tempfile._get_candidate_names())
    defult_tmp_dir = tempfile.gettempdir()
    return os.path.join(defult_tmp_dir, temp_name)


def strtimestamp():
    """
    Get timestamp as string.
    :return: string
    """
    timestamp_formatter = '%Y%m%d%H%M%S'
    time = datetime.datetime.now().strftime(timestamp_formatter)
    return str(time)


def remove_shp(source):
    source = unicode(os.path.abspath(source))
    if os.path.isfile(source):
        dirname = unicode(os.path.dirname(source))
        basename = unicode(os.path.splitext(os.path.basename(source))[0])

        for ext in ('dbf', 'prj', 'qpj', 'shp', 'shx', 'cpg'):
            try:
                shp_file = unicode(os.path.join(dirname, unicode(basename + unicode('.' + ext))))
                if os.path.isfile(shp_file):
                    os.remove(shp_file)
            except Exception as e:
                __logger.error(u'Falha ao remover arquivo "{}": {}'.format(source, unicode(e)))
