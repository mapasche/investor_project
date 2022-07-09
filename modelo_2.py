import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import statsmodels.api as sm
import datetime as dt
from copy import deepcopy
from matplotlib.dates import date2num, HourLocator, MinuteLocator, DayLocator, MonthLocator
from sklearn.preprocessing import PolynomialFeatures

import parametros as pr
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
                print(f"mean: {mean}")

                low_threshold = round(mean - mean * pr.interest_percent * pr.low_threshold_amplifier / 100, 4)
                for wallet in self.info_base.wallets:
                    wallet.low_threshold = low_threshold
                ###############################################

            else:
                #obtener el promedio
                last_date = self.info_base.last_date()
                initial_date = last_date - pr.time_backwards_of_low_threshold_analysis

                mean = self.info_base.mean_in_dates(initial_date, last_date)
                print(f"mean: {mean}")

                low_threshold = round(mean - mean * pr.interest_percent * pr.low_threshold_amplifier / 100, 4)
                for wallet in self.info_base.wallets:
                    wallet.low_threshold = low_threshold

    def high_threshold_calculator (self, type_threshold, last_exchange_price):
        if type_threshold == "average":
            return last_exchange_price + last_exchange_price * pr.interest_percent / 100 * 2.2
    
    def curve_regression(self, init_date, last_date):
        data = deepcopy(self.info_base.df.loc[(last_date >= self.info_base.df.date) & (init_date <= self.info_base.df.date)])
        data['time'] = np.arange(len(data.date))
        
        polynomial_features = PolynomialFeatures(degree = 2)
        X = data.loc[:, ['time']]
        X.dropna(inplace = True)
        X = polynomial_features.fit_transform(X)
        X = sm.add_constant(X)
        y = data.loc[:, 'price']

        #train en ordinary least square
        model = sm.OLS(y, X)
        results = model.fit()
        return results
        
        




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
            last_date = self.info_base.last_date()

            #results OLS degree 2.  el acompañador del x2 es el params[2]
            results_OLS_2 = self.curve_regression(last_date - pr.time_backwards_of_cond_low_high_curve_regression, last_date)
            curve_regression_x2_value = results_OLS_2.params[2]

            #set lowthreshold
            self.set_low_threshold_in_wallets(pr.type_of_low_threshold)


            #si es que estamos considerando interes
            if pr.with_interest:


                #print(f"Last exchange price: {last_exchange_price}")
                for i, wallet in enumerate(self.info_base.wallets):
                    #print(f"wallet {i} low threshold: {wallet.low_threshold}  amount dolar: {wallet.amount_dolar}")

                    if wallet.low_threshold > last_exchange_price:

                        if wallet.have_dolar:

                            if curve_regression_x2_value > pr.min_value_x2_curve_regression:

                                wallet.buy_coin(last_exchange_price)

                                #set highthreshold
                                wallet.high_threshold = self.high_threshold_calculator(pr.type_of_low_threshold, last_exchange_price)


                                #send the information to graph
                                df_graph_buy_sell = pd.read_csv(pr.graph_info_buy_sell_location)
                                df_graph_buy_sell.date = pd.to_datetime(df_graph_buy_sell.date)
                                new_data = {'date' : [last_date], 'action' : ["buy"], "param0" : [results_OLS_2.params[0]], "param1" : [results_OLS_2.params[2]], "param2" : [results_OLS_2.params[2]]}
                                append_df = pd.DataFrame(new_data)
                                append_df.date = pd.to_datetime(append_df.date)
                                df_graph_buy_sell = df_graph_buy_sell.append(append_df, ignore_index=True)
                                df_graph_buy_sell.to_csv(pr.graph_info_buy_sell_location, index=None)

                                return "buy"


                
                    elif wallet.high_threshold < last_exchange_price:

                        if wallet.have_coin:

                            if curve_regression_x2_value < -1 * pr.min_value_x2_curve_regression:

                                wallet.sell_coin(last_exchange_price)


                                df_graph_buy_sell = pd.read_csv(pr.graph_info_buy_sell_location)
                                df_graph_buy_sell.date = pd.to_datetime(df_graph_buy_sell.date)
                                new_data = {'date' : [last_date], 'action' : ["sell"], "param0" : [results_OLS_2.params[0]], "param1" : [results_OLS_2.params[2]], "param2" : [results_OLS_2.params[2]]}
                                append_df = pd.DataFrame(new_data)
                                append_df.date = pd.to_datetime(append_df.date)
                                df_graph_buy_sell = df_graph_buy_sell.append(append_df, ignore_index=True)
                                df_graph_buy_sell.to_csv(pr.graph_info_buy_sell_location, index=None)
                                
                                return "sell"



                    """elif wallet.last_bought_price - wallet.last_bought_price * pr.interest_percent / 100 > last_exchange_price:

                        if wallet.have_coin:
                            
                            wallet.sell_coin(last_exchange_price)


                            df_graph_buy_sell = pd.read_csv(pr.graph_info_buy_sell_location)
                            df_graph_buy_sell.date = pd.to_datetime(df_graph_buy_sell.date)
                            new_data = {'date' : [last_date], 'action' : ["sell"], "param0" : [results_OLS_2.params[0]], "param1" : [results_OLS_2.params[2]], "param2" : [results_OLS_2.params[2]]}
                            append_df = pd.DataFrame(new_data)
                            append_df.date = pd.to_datetime(append_df.date)
                            df_graph_buy_sell = df_graph_buy_sell.append(append_df, ignore_index=True)
                            df_graph_buy_sell.to_csv(pr.graph_info_buy_sell_location, index=None)

                            return "sell"""
            

            #sin interes ----------------------------------------------------------------------------------------------
            else:


                for i, wallet in enumerate(self.info_base.wallets):

                    if wallet.have_dolar:

                        if curve_regression_x2_value > pr.min_value_x2_curve_regression:

                            wallet.buy_coin(last_exchange_price)

                            #send the information to graph
                            send_information_2_graph(action = "buy", results_x2 = results_OLS_2, last_date = last_date)

                            return "buy"


                
                    elif wallet.high_threshold < last_exchange_price:

                        if wallet.have_coin:

                            if curve_regression_x2_value < -1 * pr.min_value_x2_curve_regression:

                                wallet.sell_coin(last_exchange_price)
                                
                                #send the information to graph
                                send_information_2_graph(action = "sell", results_x2 = results_OLS_2, last_date = last_date)
                                
                                return "sell"



                    elif wallet.last_bought_price - wallet.last_bought_price * pr.interest_percent / 100 > last_exchange_price:

                        if wallet.have_coin:
                            
                            wallet.sell_coin(last_exchange_price)

                            #send the information to graph
                            send_information_2_graph(action = "sell", results_x2 = results_OLS_2, last_date = last_date)

                            return "sell"""                









        #si pasa nada
        return None



