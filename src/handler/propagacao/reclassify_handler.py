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


class ReclassifyHandler(Handler):

    def handle(self, **kwargs):
        self.logger.debug('>>> Handler: 7...')

        rasters_name = kwargs['rasters_name']
        clip_layers = kwargs['clip_layers']
        objeto = kwargs['objeto']

        reclass_layers = objeto.reclassify(clip_layers, rasters_name)
        if len(reclass_layers) == 5:
            kwargs['reclass_layers'] = reclass_layers
            self.next(**kwargs)
        else:
            self.error = 'Fail to reclassify rasters'
            self.logger.error(self.error)
            raise RuntimeError(self.error)
