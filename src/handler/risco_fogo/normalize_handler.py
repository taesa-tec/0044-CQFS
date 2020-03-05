# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CQFS
                                 A QGIS plugin
 Criticidade à Queimadas em Faixas de Servidão
                              -------------------
        begin                : 2018-09-21
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
from ..handler import Handler
from ....src.reclass.risco_fogo_normalizacao_reclass import RiscoFogoNormalizacaoReclass
from ....src.reclassify import Reclassify
from ....src.cqfs_config import tmp_filename_without_extension
from ....src.layer_util import import_layer_qgis


class NormalizeHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 5...')

        if 'rasters_selected' not in kwargs:
            self.error = 'Selecione o raster para a normalizacao'
            self.logger.error(self.error)
            raise RuntimeError(self.error)

        
        else:
            out = tmp_filename_without_extension() + '.tif'
            rasterin = kwargs['rasters_selected'][0]

            propagacao = RiscoFogoNormalizacaoReclass(rasterin.source(), out)
            re = Reclassify(propagacao)
            re.apply()

            kwargs['raster_out_normalize'] = import_layer_qgis(out, suffix='normalize', base_layer=out)

            self.next(**kwargs)
