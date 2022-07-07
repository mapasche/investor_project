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

            self.upload_graph_info()

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
        last_date = self.info_base.last_date()
        with open(pr.buy_sell_history_location, "a", encoding="utf-8") as archive:
            archive.write(f"Action: {action} \t Total money: {self.info_base.total_money} \t Date: {last_date}\n")
            archive.write(f"Total dolar: {round(self.info_base.total_dolar, 4)} \t Total coin: {round(self.info_base.total_coin, 4)}\n")
            for i, wallet in enumerate(self.info_base.wallets):
                archive.write(f"Wallet {i}: \t Dolar: {round(self.info_base.total_dolar, 4)} \t Coin: {round(self.info_base.total_coin, 4)}\n")
            archive.write(f"\n\n")

        #send the information to graph
        df_graph_buy_sell = pd.read_csv(pr.graph_info_buy_sell_location)
        df_graph_buy_sell.date = pd.to_datetime(df_graph_buy_sell.date)
        new_data = {'date' : [last_date], 'action' : [action]}
        append_df = pd.DataFrame(new_data)
        append_df.date = pd.to_datetime(append_df.date)
        df_graph_buy_sell = df_graph_buy_sell.append(append_df, ignore_index=True)
        df_graph_buy_sell.to_csv(pr.graph_info_buy_sell_location, index=None)

        
    def upload_graph_info (self):
        last_date = self.info_base.last_date()
        initial_date = last_date - pr.time_backwards_of_low_threshold_analysis

        last_date = self.info_base.last_date()
        mean = self.info_base.mean_in_dates(initial_date, last_date)
        lowest_threshold = self.info_base.lowest_threshold()

        with open(pr.graph_info_location, "a", encoding="utf-8") as archive:
            archive.write(f"{last_date},{mean},{lowest_threshold}\n")





