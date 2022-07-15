import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import statsmodels.api as sm
import datetime as dt
from copy import deepcopy
from matplotlib.dates import date2num, HourLocator, MinuteLocator, DayLocator, MonthLocator
from sklearn.preprocessing import PolynomialFeatures
from functools import reduce
import operator

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
                #print(f"mean: {mean}")

                low_threshold = round(mean - mean * pr.interest_percent * pr.low_threshold_amplifier / 100, 4)
                for wallet in self.info_base.wallets:
                    wallet.low_threshold = low_threshold
                ###############################################

            else:
                #obtener el promedio
                last_date = self.info_base.last_date()
                initial_date = last_date - pr.time_backwards_of_low_threshold_analysis

                mean = self.info_base.mean_in_dates(initial_date, last_date)
                #print(f"mean: {mean}")

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

    
    def porcentual_dif (self, init_date, last_date):
        data = deepcopy(self.info_base.df.loc[(last_date >= self.info_base.df.date) & (init_date <= self.info_base.df.date)])
        data['lag_1'] = data["price"].shift(1)
        data.dropna(inplace = True)
        data["porcentual_dif"] = (data["price"] - data["lag_1"]) / data["price"] + 1

        return (reduce(operator.mul, data.porcentual_dif) - 1 ) * 100
        
        




    def evaluate (self):

        if pr.type_of_low_threshold == "average":           



            # mejorar modelo cuadratico aplicando una pendiente positiva


            #intentar capturar las subidas al usar el percentage dif en corto tiempo


            #agarrar el minimo en un rango de tiempo de 5 min y comparar el percentage dif para ver que tan rapido sube y luego vender cuando haya bajado harto del max
            #si se supera cierto percentage dif, hay que usar la condicion del percentage dif para ver que se esta usando el maximo provecho

            #la regresion cuadratica se esta equivocando pq toma el x2 positivo pero la curva esta subiendo y no fue un minimo

            #agregar que cuando se esta en pendiente positiva, se puede comprar. 1 min

            #agregar que solo se puede vender cuando se está sobre el precio de compra



            last_exchange_price = self.info_base.last_exchange_price
            last_date = self.info_base.last_date()

            #results OLS degree 2.  el acompañador del x2 es el params[2]
            results_OLS_2 = self.curve_regression(last_date - pr.time_backwards_of_cond_low_high_curve_regression, last_date)
            curve_regression_x2_value = results_OLS_2.params[2]

            #set lowthreshold
            self.set_low_threshold_in_wallets(pr.type_of_low_threshold)


            #percentage dif
            porcentage_dif = self.porcentual_dif(last_date - pr.time_backwards_of_cond_porcentual_dif, last_date)


            self.info_base.check_wallet_can_buy()


            print("Exchange price:", last_exchange_price)


            #si es que estamos considerando interes
            if pr.with_interest:


                #print(f"Last exchange price: {last_exchange_price}")
                for i, wallet in enumerate(self.info_base.wallets):
                    #print(f"wallet {i} low threshold: {wallet.low_threshold}  amount dolar: {wallet.amount_dolar}")

                    if wallet.low_threshold > last_exchange_price:

                        if wallet.have_dolar:

                            if curve_regression_x2_value > pr.min_value_x2_curve_regression:

                                amount_dolar = wallet.buy_coin(last_exchange_price, last_date)

                                #set highthreshold
                                wallet.high_threshold = self.high_threshold_calculator(pr.type_of_low_threshold, last_exchange_price)


                                #send the information to graph
                                send_information_2_graph(action = "buy", results_x2 = results_OLS_2, porcentual_dif = porcentage_dif, last_date = last_date)

                                return "buy", amount_dolar


                
                    elif wallet.high_threshold < last_exchange_price:

                        if wallet.have_coin:

                            if curve_regression_x2_value < -1 * pr.min_value_x2_curve_regression:

                                amount_coin = wallet.sell_coin(last_exchange_price)


                                #send the information to graph
                                send_information_2_graph(action = "sell", results_x2 = results_OLS_2, porcentual_dif = porcentage_dif, last_date = last_date)
                                
                                return "sell", amount_coin



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
                    print("Last bought price:", wallet.last_bought_price)
                    print("Sell parameter:", wallet.last_bought_price - wallet.last_bought_price * pr.stop_loss_proportion, "\n")



                    if wallet.have_dolar and wallet.can_buy:# and wallet.low_threshold > last_exchange_price:

                        if curve_regression_x2_value > pr.min_value_x2_curve_regression:

                            amount_dolar = wallet.buy_coin(last_exchange_price)

                            #set highthreshold
                            wallet.high_threshold = self.high_threshold_calculator(pr.type_of_low_threshold, last_exchange_price)

                            #send the information to graph
                            send_information_2_graph(action = "buy", results_x2 = results_OLS_2, porcentual_dif = porcentage_dif, last_date = last_date)

                            return "buy", amount_dolar

                

                    elif pr.with_high_threshold:

                        if wallet.high_threshold < last_exchange_price:

                            if wallet.have_coin:# and wallet.high_threshold < last_exchange_price:

                                if curve_regression_x2_value < -1 * pr.min_value_x2_curve_regression:

                                    amount_coin = wallet.sell_coin(last_exchange_price)
                                    
                                    #send the information to graph
                                    send_information_2_graph(action = "sell", results_x2 = results_OLS_2, porcentual_dif = porcentage_dif, last_date = last_date)
                                    
                                    return "sell", amount_coin
                    



                        elif wallet.last_bought_price - wallet.last_bought_price * pr.stop_loss_proportion > last_exchange_price:

                            if wallet.have_coin:
                                
                                amount_coin = wallet.sell_coin(last_exchange_price, last_date)
                                wallet.set_wallet_cant_buy()

                                #send the information to graph
                                send_information_2_graph(action = "sell", results_x2 = results_OLS_2, porcentual_dif = porcentage_dif, last_date = last_date)
                                print(wallet.last_bought_price - wallet.last_bought_price * pr.stop_loss_proportion)

                                return "sell", amount_coin                

                    elif not pr.with_high_threshold:


                        if wallet.have_coin:# and wallet.high_threshold < last_exchange_price:
                            

                            if curve_regression_x2_value < -1 * pr.min_value_x2_curve_regression:

                                amount_coin = wallet.sell_coin(last_exchange_price)
                                
                                #send the information to graph
                                send_information_2_graph(action = "sell", results_x2 = results_OLS_2, porcentual_dif = porcentage_dif, last_date = last_date)
                                
                                return "sell", amount_coin
                    

                            elif wallet.last_bought_price - wallet.last_bought_price * pr.stop_loss_proportion > last_exchange_price:

                                    
                                    amount_coin = wallet.sell_coin(last_exchange_price, last_date)
                                    wallet.set_wallet_cant_buy()

                                    #send the information to graph
                                    send_information_2_graph(action = "sell", results_x2 = results_OLS_2, porcentual_dif = porcentage_dif, last_date = last_date)
                                    print(wallet.last_bought_price - wallet.last_bought_price * pr.stop_loss_proportion, "sell por bajo stop loss")

                                    return "sell", amount_coin        

        #si pasa nada
        return None, None



