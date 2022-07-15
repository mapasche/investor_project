from functions import *

import datetime as dt
import pandas as pd
import parametros as pr


class Wallet:
    def __init__(self, amount_dolar = 0):
        self.__amount_dolar = amount_dolar
        self.__amount_coin = 0

    
    def buy_coin(self, exchange_price, amount_dolar):
        amount_coin = dolar_2_coin(amount_dolar, exchange_price)
        self.amount_dolar -= amount_dolar
        self.amount_coin += amount_coin

    def sell_coin(self, exchange_price, amount_coin):
        amount_dolar = coin_2_dolar(amount_coin, exchange_price)
        self.amount_dolar += amount_dolar
        self.amount_coin -= amount_coin
        

    @property
    def amount_dolar (self):
        return self.__amount_dolar
    
    @amount_dolar.setter 
    def amount_dolar(self, setter):
        if setter < 0 - pr.epsilon:
            raise Exception("Se está seteando una cantidad de USD negativa")
        elif setter < 0:
            self.__amount_dolar = 0
        else:
            self.__amount_dolar = setter

    @property
    def amount_coin (self):
        return self.__amount_coin
    
    @amount_coin.setter
    def amount_coin(self, setter):
        if setter < 0 - pr.epsilon:
            raise Exception("Se está seteando una cantidad de BTC negativa")
        elif setter < 0:
            self.__amount_coin = 0
        else:
            self.__amount_coin = setter



class InfoWallet(Wallet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.have_coin = False
        self.have_dolar = False
        self.last_bought_price = 0
        self.high_threshold = 0
        #self.comprar_vender = False
        self.low_threshold = 0
        self.last_bought_price = -1
        self.last_sell_date = None
        self.can_buy = True
        self.confirm_have_coin()

    def set_wallet_cant_buy (self):
        self.can_buy = False
    
    def set_wallet_can_buy (self):
        self.can_buy = True

    def confirm_have_coin(self):
        if self.amount_coin > pr.epsilon:
            self.have_coin = True
        else:
            self.have_coin = False
        
        if self.amount_dolar > pr.epsilon:
            self.have_dolar = True
        else:
            self.have_dolar = False

    def buy_coin(self, exchange_price, amount_dolar = -1):

        if amount_dolar == -1:
            amount_dolar = self.amount_dolar

        #aplicamos interes
        if pr.with_interest:
            amount_dolar_with_interest = amount_dolar - amount_dolar * pr.interest_percent / 100
        else:
            amount_dolar_with_interest = amount_dolar
        self.last_bought_price = exchange_price
        self.last_sell_date = None
        amount_coin = dolar_2_coin(amount_dolar_with_interest, exchange_price)
        self.amount_dolar -= amount_dolar
        self.amount_coin += amount_coin
        self.confirm_have_coin()
        
        return amount_dolar


    def sell_coin(self,  exchange_price, last_date = None, amount_coin = -1):
        if amount_coin == -1:
            amount_coin = self.amount_coin
        
        #aplicamos interes
        if pr.with_interest:
            amount_coin_with_interest = amount_coin - amount_coin * pr.interest_percent / 100
        else:
            amount_coin_with_interest = amount_coin

        amount_dolar = coin_2_dolar(amount_coin_with_interest, exchange_price)
        self.amount_dolar += amount_dolar
        self.amount_coin -= amount_coin

        self.last_bought_price = -1
        self.last_sell_date = last_date
        self.confirm_have_coin()

        return amount_coin



class InfoBase:
    def __init__(self, amount_dolar_initially = 100, *args, **kwargs):
        
        self.wallets = [InfoWallet(amount_dolar_initially)]
        self.have_coin = False
        self.__df = None
        self.last_exchange_price = 0
        self.total_dolar = 0
        self.total_coin = 0
        self.total_money = self.set_total_money()
        self.last_exchange_price = None
        self.last_exchange_date = None

    @property
    def df(self):
        return self.__df

    @df.setter
    def df(self, value):
        if not type(value) == pd.core.frame.DataFrame:
            print("MEGA ERROR, el df que estas intentando setter en el INFOBASE no es dataframe")

        self.__df = value
        self.__df.date = pd.to_datetime(self.__df.date)
        self.set_last_exchange_price()
    
    def set_total_money (self):
        self.set_total_coin()
        self.set_total_dolar()
        self.total_money = self.total_dolar + self.total_coin * self.last_exchange_price

    def set_total_dolar(self):
        total = 0
        for wallet in self.wallets:
            total += wallet.amount_dolar
        self.total_dolar = total

    def set_total_coin (self):
        total = 0
        for wallet in self.wallets:
            total += wallet.amount_coin
        self.total_coin = total

    def set_last_exchange_price (self):
        try:
            self.last_exchange_price = self.df.iloc[-1].price
        except Exception as e:
            return e

    def set_last_exchange_date (self):
        try:
            self.last_exchange_date = self.df.iloc[-1].date
        except Exception as e:
            return e
    
    def mean_in_dates (self, init_date, last_date = dt.datetime.now()):
        try:
            return round(self.df.loc[(last_date >= self.df.date) & (self.df.date >= init_date)]["price"].mean(), 4)
        except Exception as e:
            return e

    def last_date (self):
        date = self.df.iloc[-1].date
        return date

    def confirm_have_coin (self):

        for wallet in self.wallets:
            if wallet.have_coin:
                self.have_coin = True
                break
        
        self.have_coin = False

    def lowest_threshold (self):  
        return min(self.wallets, key= lambda x: x.low_threshold).low_threshold

    def check_wallet_can_buy(self):
        self.set_last_exchange_date()

        for wallet in self.wallets:

            if not wallet.last_sell_date == None:
                amount_time_pass = self.last_exchange_date - wallet.last_sell_date

                if amount_time_pass >= pr.time_not_buy:
                    wallet.set_wallet_can_buy()
                else:
                    wallet.set_wallet_cant_buy()












