from classes import *
from functions import *
import threading
import parametros as pr
import modelo_2 as md



class LogicMoney(threading.Thread):
    def __init__(self , db_location, event_turn_of_db, event_turn_of_logic, *arg, **kwargs):
        super().__init__(**kwargs)

        self.db_location = db_location
        self.event_turn_of_db = event_turn_of_db
        self.event_turn_of_logic = event_turn_of_logic
        #self.wallet = Wallet()
        self.model = md.Oscilations()
        self.info_base = InfoBase()


    def run(self):
        
        while True:
            #recibe el event
            self.event_turn_of_logic.wait()
            self.event_turn_of_logic.clear()

            self.download_db()

            action, amount, exchange_price = self.model.evaluate(self.df)

            if action == "buy":
                self.buy_coin(amount, exchange_price)
            elif action == "sell":
                self.sell_coin(amount, exchange_price)
            else:
                pass
            
            #Manda event
            self.event_turn_of_db.set()  

    

    """def buy_coin(self, amount_dolar, exchange_price):
        self.wallet.buy_coin( exchange_price, amount_dolar)

    def sell_coin(self, amount_btc, exchange_price):
        self.wallet.sell_coin(exchange_price, amount_btc)"""

    def download_db(self):
        self.info_base.df = pd.read_csv(pr.artificial_db_location)
        self.info_base.df.date = pd.to_datetime(self.df.date)
        return self.df




