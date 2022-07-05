from classes import *
from functions import *
import pandas as pd
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
        self.info_base = InfoBase()
        self.model = md.Oscilations(self.info_base)     


    def run(self):
        
        while True:
            #recibe el event
            self.event_turn_of_logic.wait()
            self.event_turn_of_logic.clear()

            self.download_db()
            
            action = self.model.evaluate()

            last_exchange_price = self.info_base.last_exchange_price

            if not action == None:
                self.info_base.set_total_money()
                self.upload_action_to_history(action)

            #Manda event
            self.event_turn_of_db.set()  

    

    """def buy_coin(self, amount_dolar, exchange_price):
        self.wallet.buy_coin( exchange_price, amount_dolar)

    def sell_coin(self, amount_btc, exchange_price):
        self.wallet.sell_coin(exchange_price, amount_btc)"""

    def download_db(self):
        self.info_base.df = pd.read_csv(pr.artificial_db_location)
        return self.info_base.df

    def upload_action_to_history (self, action):
        with open(pr.buy_sell_history_location, "a", encoding="utf-8") as archive:
            archive.write(f"Action: {action} \t Total money: {self.info_base.total_money}\n")
            archive.write(f"Total dolar: {round(self.info_base.total_dolar, 4)} \t Total coin: {round(self.info_base.total_coin, 4)}\n")
            for i, wallet in enumerate(self.info_base.wallets):
                archive.write(f"Wallet {i}: \t Dolar: {round(self.info_base.total_dolar, 4)} \t Coin: {round(self.info_base.total_coin, 4)}\n")
            archive.write(f"\n\n")




