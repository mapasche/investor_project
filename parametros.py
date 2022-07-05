import datetime as dt

interest_percent = 0.1

#location of archives
db_location = "datos/info.csv"
artificial_db_location = "datos/info_art.csv"
buy_sell_history_location = "resultados/buy_sell_history.txt"

initial_date = dt.datetime(2022, 6, 1, 14)
final_date = dt.datetime(2022, 7, 5, 17)

epsilon = 0.01


#parameters model of oscilations

type_of_low_threshold = "average"
time_backwards_of_low_threshold_analysis = dt.timedelta(hours=4)





#text of the program
text_total_amount_money = "Total money: {money}"