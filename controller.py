# -*- coding: utf-8 -*-

from configinit.settings import Settings
from library.sarimax import Sarimax

'''
    File name: controller.py
    Project: EletrobrasQ
    Python Version: 3.6.0
'''
__author__ = "Tiago S. Buzato & Alex Pessoa"
__version__ = "0.1"
__email__ = "tiago.buzato@climatempo.com.br & alexpessoa@climatempo.com.br"
__status__ = "Development"


# Tag das Mensagens:
# [I] -> Informacao
# [A] -> Aviso/Alerta
# [E] -> Erro

def run(rootpath, logger, settings: Settings, verbose=False):
    print('[I] Starting sarimax model for prediction of {sector}.'.format(sector=settings.sector))
    logger.info('Starting sarimax model for prediction of {sector}.'.format(sector=settings.sector))

    Sarimax(settings.p1, settings.d1, settings.q1, settings.p2, settings.d2, settings.q2, settings.sector,
            settings.listvariables, settings.vtarget, settings.vexog, settings.parallel, rootpath, logger,
            verbose).run()

    return
