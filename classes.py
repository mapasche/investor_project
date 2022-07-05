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
        self.df = None

    

    def set_low_threshold (self):

        if type_of_low_threshold == "average":
            self.confirm_have_coin()

            if self.have_coin:
                #obtener el valor mas bajo comprado en las wallets
                pass
            else:
                #obtener el promedio
                pass
    
    def mean_in_dates (self, init_date, last_date = dt.datetime.now()):
        try:
            return self.df.loc[(last_date >= self.df.date) & (self.df.date >= init_date)]["price"].mean()
        except Exception as e:
            return e


    def confirm_have_coin (self):

        for wallet in self.wallets:
            if wallet.have_coin:
                self.have_coin = True
                break












