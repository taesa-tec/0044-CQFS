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
from handler import Handler
from propagaca_handler import PropagacaoHandler
from riscofogo_handler import RiscoFogoHandler
from ignicao_handler import IgnicaoHandler
from criticidade_handler import CriticidadeHandler
from vulnerabilidade_handler import VulnerabilidadeHandler


class TabHandler(Handler):

    def handle(self, **kwargs):
        cqfs = kwargs['cqfs']
        index = cqfs.dlg.tab_widget.currentIndex()

        if index == 0:
            self.logger.debug('Running "Propagacao" -> {}'.format(str(kwargs)))
            handler = PropagacaoHandler()
            handler.handle(**kwargs)
        elif index == 1:
            self.logger.debug('Running "Ignicao" -> {}'.format(str(kwargs)))
            handler = IgnicaoHandler()
            handler.handle(**kwargs)
        elif index == 3:
            self.logger.debug('Running "Vulnerabilidade" -> {}'.format(str(kwargs)))
            handler = VulnerabilidadeHandler()
            handler.handle(**kwargs)
        elif index == 2:
            handler = RiscoFogoHandler()
            handler.handle(**kwargs)
            self.logger.debug('Running "Risco de Fogo" -> {}'.format(str(kwargs)))
        elif index == 4:
            self.logger.debug('Running "Criticidade" -> {}'.format(str(kwargs)))
            handler = CriticidadeHandler()
            handler.handle(**kwargs)


        else:
            raise ValueError('Handler {} not found.'.format(str(index)))
