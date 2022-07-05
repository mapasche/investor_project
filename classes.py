import datetime as dt

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
        

    @amount_dolar
    def amount_dolar (self):
        return self.__amount_dolar
    
    @setter.amount_dolar
    def amount_dolar(self, setter):
        if setter < 0 - pr.epsilon:
            raise Exception("Se está seteando una cantidad de USD negativa")
        elif setter < 0:
            self.__amount_dolar = 0
        else:
            self.__amount_dolar = round(setter, 5)

    @amount_coin
    def amount_coin (self):
        return self.__amount_coin
    
    @setter.amount_coin
    def amount_coin(self, setter):
        if setter < 0 - pr.epsilon:
            raise Exception("Se está seteando una cantidad de BTC negativa")
        elif setter < 0:
            self.__amount_coin = 0
        else:
            self.__amount_coin = round(setter, 2)



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
        amount_dolar_with_interest = amount_dolar - amount_dolar * pr.interest_percent / 100
        
        amount_coin = dolar_2_coin(amount_dolar_with_interest, exchange_price)
        self.amount_dolar -= amount_dolar
        self.amount_coin += amount_coin
        self.confirm_have_coin()
        self.last_bought_price = exchange_price

        return amount_coin



    def sell_coin(self,  exchange_price, amount_coin = -1):
        if amount_coin == -1:
            amount_coin = self.amount_coin
        
        #aplicamos interes
        amount_coin_with_interest = amount_coin - amount_coin * pr.interest_percent / 100

        amount_dolar = coin_2_dolar(amount_coin_with_interest, exchange_price)
        self.amount_dolar += amount_dolar
        self.amount_coin -= amount_coin

        self.last_bought_price = -1

        self.confirm_have_coin()





class InfoBase:
    def __init__(self, amount_dolar_initially = 100, *args, **kwargs):
        
        self.wallets = [InfoWallet(amount_dolar_initially)]
        self.have_coin = False
        self.__df = None
        self.low_threshold = None
        self.last_exchange_price = 0

    @df
    def df(self):
        return self.__df

    @setter.df
    def df(self, value):
        if not type(value) == pd.core.frame.DataFrame:
            print("MEGA ERROR, el df que estas intentando setter en el INFOBASE no es dataframe")

        self.__df = value
        self.__df = pd.to_datetime(self.__df.date)
        self.set_last_exchange_price()
    

    def total_money (self):

        if precio == 0:
            precio  = self.df.iloc[-1,].Price
        self.dinero_total = self.dinero + self.crypto * precio

    def set_low_threshold (self):

        if pr.type_of_low_thrseshold == "average":
            self.confirm_have_coin()

            if self.have_coin:
                #obtener el valor mas bajo comprado en las wallets
                pass
                
                ###############################################
                #### Por ahora los dos casos serán iguales ####
                ###############################################
                last_date = last_date()
                mean = mean_in_dates(last_date - pr.time_backwards_of_low_threshold_analysis, last_date)
                low_threshold = mean - mean * pr.interest_percent / 100
                for wallet in self.wallets:
                    wallet.low_threshold = low_threshold
                ###############################################

            else:
                #obtener el promedio
                last_date = last_date()
                mean = mean_in_dates(last_date - pr.time_backwards_of_low_threshold_analysis, last_date)

                low_threshold = mean - mean * pr.interest_percent / 100
                for wallet in self.wallets:
                    wallet.low_threshold = low_threshold

    def set_last_exchange_price (self):
        try:
            self.last_exchange_price = self.df.iloc[-1].price
        except Exception as e:
            return e
    
    def mean_in_dates (self, init_date, last_date = dt.datetime.now()):
        try:
            return round(self.df.loc[(last_date >= self.df.date) & (self.df.date >= init_date)]["price"].mean(), 4)
        except Exception as e:
            return e

    def last_date (self):
        return self.df.iloc[-1].date

    def confirm_have_coin (self):

        for wallet in self.wallets:
            if wallet.have_coin:
                self.have_coin = True
                break
        
        self.have_coin = False












