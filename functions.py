import parametros as pr
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import parametros as pr
from datetime import datetime, timedelta
from matplotlib.dates import date2num, HourLocator, MinuteLocator, DayLocator, MonthLocator, AutoDateLocator, AutoDateFormatter
from sklearn.preprocessing import PolynomialFeatures
import statsmodels.api as sm


def coin_2_dolar (amount_coin, market_price_in_dolar):
    return amount_coin * market_price_in_dolar

def dolar_2_coin(amount_dolar, market_price_in_dolar):
    return amount_dolar / market_price_in_dolar


def send_information_2_graph(action, results_x2, last_date):
    df_graph_buy_sell = pd.read_csv(pr.graph_info_buy_sell_location, parse_dates=['date'])
    new_data = {'date' : [last_date], 'action' : [action], "param0" : [results_x2.params[0]], "param1" : [results_x2.params[1]], "param2" : [results_x2.params[2]]}
    append_df = pd.DataFrame(new_data)
    append_df.date = pd.to_datetime(append_df.date)
    df_graph_buy_sell = df_graph_buy_sell.append(append_df, ignore_index=True)
    df_graph_buy_sell.to_csv(pr.graph_info_buy_sell_location, index=None)






def show_final_graph():

    if pr.graph_with_volume:
        figure, axs = plt.subplots(2, 1, figsize = (10, 10))
    else:
        figure, axs = plt.subplots(1, 1, figsize = (10, 10))

    #descargamos la informacion
    df = pd.read_csv(pr.artificial_db_location, parse_dates=["date"])
    df['time'] = np.arange(len(df.date))
    df_graph = pd.read_csv("resultados/graph_info.csv")
    df_graph.date = pd.to_datetime(df_graph.date)
    df_buy_sell = pd.read_csv(pr.graph_info_buy_sell_location)
    df_buy_sell.date = pd.to_datetime(df_buy_sell.date)
    init_date = df.date.iloc[0]
    last_date = df.date.iloc[-1]


    if pr.graph_with_volume:
        axs[0].plot_date(x = df.date, y = df.price, linestyle='-', markersize = 0.01, label="Price")
        axs[0].plot_date(x= df_graph.date, y = df_graph.average, linestyle='-', markersize = 0.01, label="MA")
        axs[0].plot_date(x= df_graph.date, y = df_graph.low_threshold, linestyle='-', markersize = 0.01, label="MA - Interest")
        setear_visualizador_eje_x(axs[0], init_date, last_date)

        axs[1].plot_date(x= df.date, y = df.volume, linestyle='-', color="purple", markersize = 0.01, label="volumen")
        axs_1v2 = axs[1].twinx()
        axs_1v2.plot_date(x= df.date, y = df.trades, linestyle='-', color="gray", markersize = 0.1, label="trades")
        setear_visualizador_eje_x(axs[1], init_date, last_date)

        #vertical lines of buy and sell
        df_buy_sell.apply(lambda row: axs[0].axvline(x=row.date, linewidth=1, color="red") if row.action == "buy" else axs[0].axvline(x=row.date, linewidth=1, color="green") , axis=1)

        #graficar las cuadraticas
        for i in df_buy_sell.index:
            data, y_pred = create_cuadratic(df, df_buy_sell, pr.time_backwards_of_cond_low_high_curve_regression, i)
            axs[0].plot_date(x = data.date, y = y_pred, linestyle='-', markersize = 0.01, color="purple")
        
        axs[1].grid(True)
        axs[0].grid(True)
    
    else:
        axs.plot_date(x = df.date, y = df.price, linestyle='-', markersize = 0.01, label="Price")
        axs.plot_date(x= df_graph.date, y = df_graph.average, linestyle='-', markersize = 0.01, label="MA")
        axs.plot_date(x= df_graph.date, y = df_graph.low_threshold, linestyle='-', markersize = 0.01, label="MA - Interest")
        setear_visualizador_eje_x(axs, init_date, last_date)

        #vertical lines of buy and sell
        df_buy_sell.apply(lambda row: axs.axvline(x=row.date, linewidth=1, color="red") if row.action == "buy" else axs.axvline(x=row.date, linewidth=1, color="green") , axis=1)

        #graficar las cuadraticas
        for i in df_buy_sell.index:
            data, y_pred = create_cuadratic(df, df_buy_sell, pr.time_backwards_of_cond_low_high_curve_regression, i)
            axs.plot_date(x = data.date, y = y_pred, linestyle='-', markersize = 0.01, color="purple", alpha = 0.5)

        axs.grid(True)
        
    


    #legends
    #fig = plt.gcf()
    figure.legend(loc=1)
    figure.tight_layout()
    #plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")

    plot_save(pr.graph_location)
    plt.show()


def create_cuadratic (df, df_buy_sell, time_backwards, index_buy_sell):

    init_date = df_buy_sell.date[index_buy_sell] - time_backwards
    last_date = df_buy_sell.date[index_buy_sell]

    data = df.loc[(last_date >= df.date) & (init_date <= df.date)]

    polynomial_features = PolynomialFeatures(degree = 2)
    X = data.loc[:, ['time']]
    X.dropna(inplace = True)
    X = polynomial_features.fit_transform(X)
    X = sm.add_constant(X)
    y = data.loc[:, 'price']

    #train en ordinary least square
    model = sm.OLS(y, X)
    results = model.fit()

    last_date_predict = last_date + time_backwards
    data = df.loc[(last_date_predict >= df.date) & (init_date <= df.date)]

    X = data.loc[:, ['time']]
    X.dropna(inplace = True)
    X = polynomial_features.fit_transform(X)
    X = sm.add_constant(X)

    y_pred = results.predict(X)
    return data, y_pred


def setear_visualizador_eje_x(ax, init_date, last_date):
    locator = AutoDateLocator()

    #setear el visualizador del eje x
    if last_date - init_date <= timedelta(hours=1):
        ax.xaxis.set_major_locator(MinuteLocator(byminute=(0, 15, 30, 45)))
    elif last_date - init_date <= timedelta(hours=2):
        ax.xaxis.set_major_locator(MinuteLocator(byminute=(0, 30)))
    elif last_date - init_date <= timedelta(hours=3):
        ax.xaxis.set_major_locator(HourLocator(byhour=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 ,20 ,21, 22, 23)))
    elif last_date - init_date <= timedelta(hours=6):
        ax.xaxis.set_major_locator(HourLocator(byhour=(0, 2, 4, 6, 8, 10, 12, 14, 16, 18 , 20, 22)))
    elif last_date - init_date <= timedelta(hours=12):
        ax.xaxis.set_major_locator(HourLocator(byhour=(0, 3, 6, 9, 12, 15, 18, 21)))
    elif last_date - init_date <= timedelta(hours=24):
        ax.xaxis.set_major_locator(HourLocator(byhour=(0, 6, 12, 18)))
    elif last_date - init_date <= timedelta(days=4):
        ax.xaxis.set_major_locator(HourLocator(byhour=(0, 12)))
    elif last_date - init_date <= timedelta(days=7):
        ax.xaxis.set_major_locator(locator)
        #ax.xaxis.set_major_locator(DayLocator(bymonthday=(0, 2, 4, 6)))
    elif last_date - init_date <= timedelta(days=31):
        ax.xaxis.set_major_locator(DayLocator(byhour=(0, 7, 14, 21, 28)))
    else:
        ax.xaxis.set_major_locator(MontLocator())

def plot_labels ():
    plt.xlabel('Fechas')    
    plt.ylabel('Precio en USD $')
    plt.title("USD-BTC")

def plot_size ():
    plt.figure(figsize=(10, 10))

def plot_save( direction ):
    plt.savefig(direction, dpi = 1000)

