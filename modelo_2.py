import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import json
import statsmodels.api as sm
from datetime import datetime, timedelta
from matplotlib.dates import date2num, HourLocator, MinuteLocator, DayLocator, MonthLocator
from sklearn.preprocessing import PolynomialFeatures

import parametros
from classes import *
from functions import *



class Oscilations:
    def __init__(self, info_base):
        self.info_base = info_base

    
    
    def evaluate (self):




        if pr.type_of_low_thrseshold == "average":
            


            ################################################################
            #
            # 1 - ver si low_threshold mayor al precio de mercado
            #       - comprar
            #               -setear highthreshold
            # 2 - ver si el high_threshold es menor al precio de mercado
            #       - vender
            #
            ################################################################ 
            last_exchange_price = self.info_base.last_exchange_price

            for wallet in self.info_base.wallets:

                if wallet.low_threshold > last_exchange_price:

                    if wallet.have_dolar:

                        wallet.buy_coin(last_exchange_price)

                        



                