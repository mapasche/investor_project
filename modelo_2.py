import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import json
import statsmodels.api as sm
import datetime as dt
from matplotlib.dates import date2num, HourLocator, MinuteLocator, DayLocator, MonthLocator
from sklearn.preprocessing import PolynomialFeatures

import parametros
from classes import *
from functions import *






class Oscilations:
    def __init__(self, info_base):
        self.info_base = info_base

    
    def set_low_threshold_in_wallets (self, type_threshold):

        if type_threshold == "average":
            self.info_base.confirm_have_coin()

            if self.info_base.have_coin:
                #obtener el valor mas bajo comprado en las wallets
                pass
                
                ###############################################
                #### Por ahora los dos casos serán iguales ####
                ###############################################
                last_date = self.info_base.last_date()
                initial_date = last_date - pr.time_backwards_of_low_threshold_analysis

                mean = self.info_base.mean_in_dates(initial_date, last_date)
                low_threshold = mean - mean * pr.interest_percent / 100
                for wallet in self.info_base.wallets:
                    wallet.low_threshold = low_threshold
                ###############################################

            else:
                #obtener el promedio
                last_date = self.info_base.last_date()
                initial_date = last_date - pr.time_backwards_of_low_threshold_analysis

                mean = self.info_base.mean_in_dates(initial_date, last_date)

                low_threshold = mean - mean * pr.interest_percent / 100
                for wallet in self.info_base.wallets:
                    wallet.low_threshold = low_threshold



    def high_threshold_calculator (self, type_threshold, last_exchange_price):
        if type_threshold == "average":
            return last_exchange_price + last_exchange_price * pr.interest_percent / 100 * 2.2
    

    def evaluate (self):

        if pr.type_of_low_threshold == "average":
            


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



            #set lowthreshold
            self.set_low_threshold_in_wallets(pr.type_of_low_threshold)
                



            for wallet in self.info_base.wallets:

                if wallet.low_threshold > last_exchange_price:

                    if wallet.have_dolar:

                        wallet.buy_coin(last_exchange_price)

                        #set highthreshold
                        wallet.high_threshold = self.high_threshold_calculator(pr.type_of_low_threshold, last_exchange_price)
                        print("Buy")

                        return "buy"


            
                elif wallet.high_threshold < last_exchange_price:

                    if wallet.have_coin:

                        wallet.sell_coin(last_exchange_price)
                        print("Sell")
                        
                        return "sell"
        
        
        #si pasa nada
        return None



