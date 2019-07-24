# -*- coding: utf-8 -*-

import sys
import warnings
import pandas as pd
import numpy as np
import multiprocessing as mp
import time
import os
from multiprocessing import Value, Lock
from numpy.linalg import LinAlgError
from sklearn.metrics import mean_squared_error, mean_absolute_error, median_absolute_error
from datetime import datetime as dt
from statsmodels.tsa.statespace.sarimax import SARIMAX
warnings.filterwarnings('ignore')

'''
    File name: arima.py
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

class Sarimax():
    def __init__(self, _param_p1, _param_d1, _param_q1, _param_p2, _param_d2, _param_q2, _sector, _listvariables,
                 _vtarget, _vexog, _parallel, _rootpath, _logger, _verbose):
        self.p1max = _param_p1
        self.d1max = _param_d1
        self.q1max = _param_q1
        self.p2max = _param_p2
        self.d2max = _param_d2
        self.q2max = _param_q2
        self.corenumber = _parallel
        self.sector = _sector
        self.vtarget = _vtarget
        self.vexog = _vexog
        self.listvariables = _listvariables
        self.logger = _logger
        self.verbose = _verbose
        self.rootpath = _rootpath
        self.file = _rootpath+'/src/Base_Vendas_Total_Jun19.xlsx'
        self.outputgraphic = _rootpath+'/outputs/graphics/'
        #self.outputQ = _rootpath+'/outputs/arimaQ/'
        self.lock = mp.Lock()
        self.counter = Value('i', 0)
        self.manager = mp.Manager()
        self.addlist = self.manager.list()

        return

    # Run Sarimax with some parameters
    def modeling(self, _model, _lenexog, _dfptestset, _dfptrain, _dfptest, _vtarget, _vexog, _p1, _q1, _d1, _p2, _q2, _d2,
                 _begindate, _enddate, _lock, _verbose):
        if _verbose:
            print('[I] Modeling to {p1}, {d1}, {q1}, {p2}, {d2}, {q2}.'.format(p1=_d1, d1=_d1, q1=_q1, p2=_p2, d2=_d2,
                                                                               q2=_q2))
        self.logger.info('Modeling to {p1}, {d1}, {q1}, {p2}, {d2}, {q2}.'.format(p1=_d1, d1=_d1, q1=_q1, p2=_p2,
                                                                                  d2=_d2, q2=_q2))
        preds = _dfptestset.copy().to_frame('y_true').assign(y_pred=np.nan)
        aic, bic = [], []

        #print(_p1, _d1, _q1, _p2, _d2, _q2)

        preds['y_pred'] = _model.predict(steps=1, exog=_dfptest[_vexog], start=_begindate, end=_enddate)
        validator = 0

        for i in range(_lenexog, len(_model.pvalues)):
            if _model.pvalues[i] <= 0.05:
                validator = validator + 1

        if validator == (len(_model.pvalues) - _lenexog):
            aic.append(_model.aic)
            bic.append(_model.bic)
            preds.dropna(inplace=True)
            mse = mean_squared_error(preds.y_true, preds.y_pred)

            testresults = {}
            testresults = [_p1, _d1, _q1, _p2, _d2, _q2, np.sqrt(mse), preds.y_true.sub(preds.y_pred).std(),
                           np.mean(aic),
                           np.std(aic), np.mean(bic), np.std(bic)]

            _lock.acquire()
            self.addlist.append(testresults)
            _lock.release()

        self.counter.value = self.counter.value + 1
        # print("############## count made {count} ##########".format(count=self.counter.value))

    def seek_parameters(self, _dfptrain, _dfptest, _vtarget, _vexog, _p1max, _d1max, _q1max, _p2max, _d2max, _q2max,
                        _lock, _begindate, _enddate, _verbose):
        if _verbose:
            print('[I] Seek parameters.')
        self.logger.info('Seek parameters.')
        # Created variable
        countmaster = 0
        dfptestset = _dfptrain[_vtarget].squeeze()
        lenexog = len(_vexog)
        procs = []
        browserprocs = mp.Process

        for p1 in range(_p1max):
            for d1 in range(_d1max):
                for q1 in range(_q1max):
                    for p2 in range(_p2max):
                        for d2 in range(_d2max):
                            for q2 in range(_q2max):

                                if p1 == 0 and d1 == 0 and q1 == 0:
                                    continue

                                try:
                                    model = SARIMAX(endog=_dfptrain[_vtarget], exog=_dfptrain[_vexog],
                                                    order=(p1, d1, q1),
                                                    seasonal_order=(p2, d2, q2, 12)).fit(disp=False)

                                except LinAlgError:
                                    continue

                                except ValueError:
                                    continue

                                countmaster = countmaster + 1

                                browserprocs = mp.Process(target=self.modeling, args=(
                                    model, lenexog, dfptestset, _dfptrain, _dfptest, _vtarget, _vexog, p1, q1, d1, p2,
                                    q2, d2, _begindate, _enddate, _lock, _verbose))
                                procs.append(browserprocs)
                                browserprocs.start()

                                #print("number of cores created {n}".format(n=len(procs)))
                                while len(procs) >= self.corenumber:
                                    for thread in procs:
                                        if not thread.is_alive():
                                            procs.remove(thread)

        browserprocs.join()
        countstep = 0

        print("################################ Entrando no while ######################################")

        while True:
            if countmaster == self.counter.value:
                print("Numero de processos criados é {n} para {count}".format(n=countmaster, count=self.counter.value))
                break
            else:
                print("Wait more a little time...")
                time.sleep(3)
                print("Numero de processos criados é {n} para {count}".format(n=countmaster, count=self.counter.value))
                countstep = countstep + 1

        if countmaster == self.counter.value:
            print("Kill all processes")
            browserprocs.terminate()
        else:
            print("Kill fail")
            browserprocs.terminate()

        return 0

    # Def to separate dataframe between train and test
    def df_train_test(self, _dfpdepartment, _listvariables, _verbose):
        if _verbose:
            print('[I] Separate between train and test the dataframe.')
        self.logger.info('Separate between train and test the dataframe.')

        # Created variable
        dfptrain = pd.DataFrame()
        dfptest = pd.DataFrame()

        # Separated data between train and test
        dfptrain, dfptest = _dfpdepartment[_listvariables], _dfpdepartment[_listvariables]  # Partial

        # Set datetime as index
        dfptrain = dfptrain.set_index('datetime')
        dfptest = dfptest.set_index('datetime')

        return dfptrain, dfptest

    # Def to create and treat two dataframes (df of department and exogenous)
    def treat_dfpdata(self, _dfpdata, _sector, _verbose):
        if _verbose:
            print('[I] Treating dataframe.')
        self.logger.info('Treating dataframe.')

        # Created variables
        dfpdep = pd.DataFrame()
        dfpexogenous = pd.DataFrame()

        # Filter dataframe to the department
        dfpdep = _dfpdata['DEPTO'] == _sector.upper()
        dfpdep = _dfpdata[dfpdep].reset_index()

        # Drop Column
        dfpdep = dfpdep.drop(['DEPTO', 'index', 'ANO', 'MES'], axis=1)

        # Rename columns
        dfpdep = dfpdep.rename(
            columns={'DATA': 'datetime', 'venda_liquida': 'venda', 'qtd_venda_liquida': 'qt_venda', 'IPCA': 'ipca',
                     'PIB': 'pib', 'Temperatura_Media': 't_media', 'Temperatura_Minima': 't_min',
                     'Dummy_Portateis': 'd_port', 'Dummy_Vestuario': 'd_vest', 'Black_Friday': 'd_bf'})

        # Sort by datetime
        dfpdep.sort_values(by=['datetime'])

        # Create dataframe of exogenous
        dfpexogenous = dfpdep[-12:]
        dfpexogenous.sort_values(by=['datetime'])
        dfpexogenous = dfpexogenous.set_index('datetime')
        dfpexogenous = dfpexogenous.drop(['venda', 'qt_venda'], axis=1)

        # Drop fields with null value
        dfpdep = dfpdep.dropna()

        # Set columns types
        dfpdep[['qt_venda', 'd_port', 'd_vest', 'd_bf']] = dfpdep[['qt_venda', 'd_port', 'd_vest', 'd_bf']].astype(
            'int64',
            copy=False)
        dfpexogenous[['d_port', 'd_vest', 'd_bf']] = dfpexogenous[['d_port', 'd_vest', 'd_bf']].astype('int64',
                                                                                                       copy=False)

        # apply log in the variables of venda, pib and ipca for the dfpdep
        for column in dfpdep.columns:
            if (('datetime' != column) and ('d_port' != column) and ('d_vest' != column) and ('d_bf' != column) and (
                    't_media' != column) and ('t_min' != column)):
                dfpdep['log_' + column] = np.log(dfpdep[column])

        # apply log in the variables of venda, pib and ipca for the dfplexogenous
        for column in dfpexogenous.columns:
            if (('datetime' != column) and ('d_port' != column) and ('d_vest' != column) and ('d_bf' != column) and (
                    't_media' != column) and ('t_min' != column)):
                dfpexogenous['log_' + column] = np.log(dfpexogenous[column])

        return dfpdep, dfpexogenous

    # Def to load xlsx file from hdfs system to pandas dataframe
    def load_file(self, _file, _verbose):
        if _verbose:
            print('[I] Load file {file} into pandas dataframe.'.format(file=_file))
        self.logger.info('Load file {file} into pandas dataframe.'.format(file=_file))

        # created variable
        opened = False

        try:
            dfpdata = pd.read_excel(_file)
        except IOError:
            print('[E] Error {error} to open file {file}.'.format(error=IOError, file=_file))
            self.logger.error('Error {error} to open file {file}.'.format(error=IOError, file=_file))
            return dfpdata, opened

        opened = True

        return dfpdata, opened

    def run(self):

        #Load file to pandas dataframe
        dfpdata, opened = self.load_file(self.file, self.verbose)

        if opened is not True:
            return
        # Treat and get dataframe of department and exogenous
        dfpdepartment, dfpexogenous = self.treat_dfpdata(dfpdata, self.sector, self.verbose)

        # Separate between train and test
        dfptrain, dfptest = self.df_train_test(dfpdepartment, self.listvariables, self.verbose)

        # Created variables of begin and end datetime to train model
        begindate = dfptest.index[0].date()
        enddate = dfptest.index[len(dfptest) - 1].date()

        # Seek the best parameters to prediction sales
        self.seek_parameters(dfptrain, dfptest, self.vtarget, self.vexog, self.p1max, self.d1max, self.q1max,
                             self.p2max, self.d2max, self.q2max, self.lock, begindate, enddate, self.verbose)

        return
