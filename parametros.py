import datetime as dt

interest_percent = 0.1

db_location = "datos/info.csv"
artificial_db_location = "datos/info_art.csv"

initial_date = dt.datetime(2022, 7, 2, 20)
final_date = dt.datetime(2022, 7, 2, 23)

epsilon = 0.01


#parametros del modelo oscilaciones

type_of_low_threshold = "average"