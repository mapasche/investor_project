import datetime as dt

api_key = 'PrRyANe2JGfKdI8doWUbJ4QTqSGb534D10u6R5PNuArbQlwtvr9g9hnzJ05tD8X3'



interest_percent = 0.1
with_interest = False
graph_with_volume = False


#location of archives
db_location = "datos/info.csv"

buy_sell_history_location = "resultados/buy_sell_history.txt"
graph_info_location = "resultados/graph_info.csv"
graph_info_buy_sell_location = "resultados/graph_info_buy_sell.csv"
graph_location = "resultados/graph.png"

main_db_location = "datos/info_2.csv"
artificial_db_location = "datos/info_2.csv"
#artificial_db_location = "datos/info_art.csv"

#año - mes - dia - hora - minuto
initial_date = dt.datetime(2022, 7, 6, 12)
final_date = dt.datetime(2022, 7, 8, 12)







time_backwards_for_art_db = dt.timedelta(hours=6)
epsilon = 0.0000001




#parameters model of oscilations

type_of_low_threshold = "average"
low_threshold_amplifier = 2
time_backwards_of_low_threshold_analysis = dt.timedelta(hours = 1)
min_value_x2_curve_regression = 0.01
time_backwards_of_cond_low_high_curve_regression = dt.timedelta(minutes=5)





#text of the program
text_total_amount_money = "Total money: {money}"





