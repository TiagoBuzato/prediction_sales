# -*- coding: utf-8 -*-

'''
    File name: tools
    Project: EletrobrasQ
    Python Version: 3.6
    Utils class that has the functions that help over the system.
'''

__author__ = "Tiago S. Buzato & Alex Pessoa"
__version__ = "0.1"
__email__ = "tiago.buzato@climatempo.com.br & alexpessoa@climatempo.com.br"
__status__ = "Development"

# Tag das Mensagens:
# [I] -> Informacao
# [A] -> Aviso/Alerta
# [E] -> Erro

import os
import logging
from datetime import datetime
import matplotlib.pyplot as plt

def logger_create(_projectname, _rootpath):

    formatter = ('%(asctime)-15s - %(name)s - %(levelname)s - %(message)s')

    logging.basicConfig(filename=(_rootpath + '/logs/'+ _projectname+'.{_data:%Y%m%d%H%M}_1.log'.
                                  format(_data=datetime.now())), level=logging.DEBUG, format=formatter)

    logger = logging.getLogger('root')

    return logger

def plot_Q(df_hist, df_fct, id_local, file_nm):
    plt.figure(figsize=(20, 10))
    plt.title("Previsao de Vazao para o Posto %s" % (id_local))
    plt.xlabel('time')
    plt.ylabel('Q')
    plt.plot(df_hist, label="Historico", color='blue', marker='o')
    plt.plot(df_fct, label='ARIMA', color='red', linestyle=':', marker='o')
    plt.legend()
    plt.savefig(file_nm)

    plt.close()

    return

def set_pd_to_csv(_outfile, _dataframe, _verbose):
    if _verbose:
        print("Saving DataFrame in csv file...")

    try:
        _dataframe.to_csv(_outfile, sep=',', encoding='utf-8', index=False)
    except Exception as escsv:
        print("Fail to save Pandas DataFrame in *.csv file. Error: ")
        print(escsv)
        return False
    return True
