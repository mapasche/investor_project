import datetime as dt

interest_percent = 0.1

#location of archives
db_location = "datos/info.csv"
artificial_db_location = "datos/info_art.csv"
buy_sell_history_location = "resultados/buy_sell_history.txt"
graph_info_location = "resultados/graph_info.csv"
graph_info_buy_sell_location = "resultados/graph_info_buy_sell.csv"
graph_location = "resultados/graph.png"

#año - mes - dia - hora - minuto
initial_date = dt.datetime(2022, 7, 6, 12)
final_date = dt.datetime(2022, 7, 6, 16)







time_backwards_for_art_db = dt.timedelta(hours=6)

epsilon = 0.0000001




#parameters model of oscilations

type_of_low_threshold = "average"
time_backwards_of_low_threshold_analysis = dt.timedelta(hours=5)





#text of the program
text_total_amount_money = "Total money: {money}"





