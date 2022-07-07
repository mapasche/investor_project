import parametros as pr
import pandas as pd
import threading
import main
import datetime as dt
from functions import *
from copy import deepcopy





#crear los threads
class ArtificialDataBaseCreator(threading.Thread):

    def __init__ (self, init_date, end_date, event_turn_of_db, event_turn_of_logic, *arg, **kwargs):
        super().__init__(**kwargs)

        #confirmar que dates esten en datetime
        if not type(init_date) == dt.datetime or not type(end_date) == dt.datetime:
            raise Exception("init o end date no son clase datetime")

        #dates in datetime
        self.init_date = init_date
        self.end_date = end_date
        self.event_turn_of_db = event_turn_of_db
        self.event_turn_of_logic = event_turn_of_logic
        self.df = None
        self.df_art = None


    def run (self):

        #Create artificial db
        data = {'date' : [], 'price' : [], 'volume' : [], 'trades' : []}
        self.df_art = pd.DataFrame(data)
        self.df_art.date = pd.to_datetime(self.df_art.date)
        self.df_art.to_csv(pr.artificial_db_location,index=None)


        #Create grahp info db
        data_2 = {'date' : [], 'average' : [], 'low_threshold' : []}
        df_graph_info = pd.DataFrame(data_2)
        df_graph_info.date = pd.to_datetime(df_graph_info.date)
        df_graph_info.to_csv(pr.graph_info_location, index=None)


        #Erase data in buy sell history
        with open(pr.buy_sell_history_location, "w", encoding="utf-8") as archive:
            archive.write("")


        #considerar primer caso
        self.download_db()
        first_index = self.df[self.df.date > self.init_date].index[0]
        index_start_art_db = self.df[self.df.date > self.init_date - pr.time_backwards_for_art_db].index[0]
        index = first_index + 1

        #init loop
        while self.df.loc[index].date < self.end_date:           

            self.update_db_art(index_start_art_db, index)

            self.event_turn_of_logic.set()
            self.event_turn_of_db.wait()
            self.event_turn_of_db.clear()

            index += 1


    def download_db (self):
        self.df = pd.read_csv(pr.db_location)
        self.df.date = pd.to_datetime(self.df.date)
        return self.df

    def update_db_art (self, first_index, second_index):
        self.df_art = deepcopy(self.df.iloc[first_index:second_index])
        self.df_art.to_csv(pr.artificial_db_location, index = None)



#crear events
event_turn_of_logic = threading.Event()
event_turn_of_db = threading.Event()



#instanciar clases de otros modulos
logic_money = main.LogicMoney(pr.artificial_db_location, event_turn_of_db, event_turn_of_logic, daemon= True)
art_db_creator = ArtificialDataBaseCreator(pr.initial_date, pr.final_date, event_turn_of_db, event_turn_of_logic, daemon=True)


#comenzar los Threads
logic_money.start()
art_db_creator.start()


art_db_creator.join()



#imprimir gráficos con la información
show_final_graph()

print("fin del programa")