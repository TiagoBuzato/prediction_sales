#!/home/buzato/anaconda3/envs/py360/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import multiprocessing
import controller
from datetime import datetime
from library.tools import logger_create
from configinit.settings import Settings

'''
    File name: service.py
    Project: Prediction Sales
    Python Version: 3.6.0
'''
__author__ = "Tiago S. Buzato"
__version__ = "0.1"
__email__ = "tiago.buzato@2rpnet.com.br"
__status__ = "Development"

# Tag das Mensagens:
# [I] -> Informacao
# [A] -> Aviso/Alerta
# [E] -> Erro

processe_number = int(multiprocessing.cpu_count())
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='''-

Descricao:
------------

''', formatter_class=argparse.RawTextHelpFormatter)


parser.add_argument("-v", "--verbose", action='store_true', dest='verbose', help="Verbose", default=False)

# Sector Sales
parser.add_argument("-s", "--sector_sales", type=str, dest='sector_sales', action='store',
                    help="Sector to prediction [portateis|lar|tecnologia|vestuario].", default=None)

parser.add_argument("-p", "--parallel", type=int, action='store', dest='parallel',
                    help='Numero de nucleos usados para paralelizar o processo',  default=8)


if __name__ == "__main__":
    wdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(wdir)

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("[I][PID.{}] Begin - {}({}).".format(os.getpid(), now, sys.argv[0]))

    # Created Variables
    args = parser.parse_args()
    sector = args.sector_sales.lower()

    if sector in ['portateis','lar','tecnologia','vestuario']:
        logger = logger_create('dpa_pred_sales_'+sector, BASE_DIR)

        logger.debug("[PID.{}] Begin - {}({}).".format(os.getpid(), now, sys.argv[0]))
        settings = Settings()

        print('Sarimax prediction for the {sector} sector.'.format(sector=sector))
        settings.sector = sector
        if args.parallel:
            settings.parallel = args.parallel

        print('[I] Into the controller.')
        logger.info('Into the controller.')
        controller.run(rootpath=BASE_DIR, logger=logger, settings=settings, verbose=args.verbose)

        logger.debug("[PID.{}] End - {}({}).".format(os.getpid(), now, sys.argv[0]))

    else:
        print('[I] It necessary to pass an acceptable parameter. Look the help with {./service.py -h}.')

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("[I][PID.{}] End - {} ({}).".format(os.getpid(), now, sys.argv[0]))

    sys.exit(0)