import multiprocessing
class Settings:
    def __init__(self):
        # Settings of Sarimax model
        self.sector = None
        self.p1 = 3
        self.d1 = 3
        self.q1 = 2
        self.p2 = 3
        self.d2 = 2
        self.q2 = 3
        self.listvariables = ['qt_venda', 'datetime', 'd_port', 'd_vest', 'log_qt_venda', 'log_pib', 'log_ipca', 'd_bf']
        self.vtarget = ['log_qt_venda']
        self.vexog = ['log_pib', 'log_ipca']
        # End settings of Arima model
        self.parallel = 4

    @property
    def vtarget(self):
        return self.__vtarget

    @vtarget.setter
    def vtarget(self, vtarget):
        self.__vtarget= vtarget

    @property
    def vexog(self):
        return self.__vexog

    @vexog.setter
    def vexog(self, vexog):
        self.__vexog = vexog

    @property
    def sector(self):
        return self.__sector

    @sector.setter
    def sector(self, sector):
        self.__sector = sector

    @property
    def listvariables(self):
        return self.__listvariables

    @listvariables.setter
    def listvariables(self, listvariables):
        self.__listvariables = listvariables

    @property
    def parallel(self):
        return self.__parallel

    @parallel.setter
    def parallel(self, cpu_num):

        if cpu_num > multiprocessing.cpu_count():
            self.__parallel = int(multiprocessing.cpu_count())/2
        else:
            self.__parallel = cpu_num