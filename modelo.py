import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import json
import statsmodels.api as sm
from datetime import datetime, timedelta
from matplotlib.dates import date2num, HourLocator, MinuteLocator, DayLocator, MonthLocator
from sklearn.preprocessing import PolynomialFeatures

from parameters import * 



class ExcepcionNoSePuedeComprar(Exception):
    pass


class MediumRegression:
    def __init__(self):
        pass


class Monedero:
    def __init__(self, dinero_inicial):
        self.dinero = dinero_inicial
        self.crypto = 0
        self.have_crypto = False
        self.last_bought_price = 0
        self.high_threshold = 0
        self.comprar_vender = False
        self.low_threshold = 0

    def comprar_monedas(self, cantidad_usd = -1, precio=0):

        
        if cantidad_usd == -1:
            cantidad_usd = self.dinero

        
        self.dinero -= cantidad_usd

        cantidad_usd_con_interes = cantidad_usd - cantidad_usd * cte_fee

        cantidad_crypto = cantidad_usd_con_interes / precio
        self.crypto += cantidad_crypto


    def vender_monedas(self, cantidad_usd_1 = -1, cantidad_crypto = -1, precio=-1):

        if precio == -1:
            precio  = self.df.iloc[-1,].Price

        if cantidad_usd_1 == -1 and cantidad_crypto == -1:
            cantidad_crypto = self.crypto
            self.crypto -= cantidad_crypto
            cantidad_crypto_con_interes = cantidad_crypto - cantidad_crypto * cte_fee
            cantidad_usd_con_interes = cantidad_crypto_con_interes * precio


        else:
            cantidad_crypto = cantidad_usd_1 / precio    
            self.crypto -= cantidad_crypto
            cantidad_crypto_con_interes = cantidad_crypto - cantidad_crypto * cte_fee
            cantidad_usd_con_interes = cantidad_usd - cantidad_usd * cte_fee

        self.dinero += cantidad_usd_con_interes

    
    def set_high_threshold(self, **kwarg):


        if modo_obtener_low_threshold == "regression":
            #L_O = r - r * fee * cte
            result_medium_last_value = kwarg["result_medium_last_value"]
            result_medium_last_value_fee = kwarg["result_medium_last_value_fee"]
            if self.have_crypto:
                self.high_threshold = self.last_bought_price + self.last_bought_price * cte_fee * cte_high_threshold
            else:
                self.high_threshold = result_medium_last_value + result_medium_last_value_fee

        
        elif modo_obtener_low_threshold == "average":
            average = kwarg["average"]
            average_fee = kwarg["average_fee"]
            if self.have_crypto:
                self.high_threshold = self.last_bought_price + cte_fee * self.last_bought_price * cte_high_threshold
            else: 
                self.high_threshold = average + average_fee



class Calculadora:

    def __init__(self, moneda, dinero_inicial, lock_db = None, event_graph = None):
        self.moneda= moneda
        self.df = None
        self.__dinero = dinero_inicial
        self.__crypto = 0.0
        self.dinero_total = 0.0
        self.have_crypto = False
        self.last_bought_price = 0
        self.last_sell_price_downfall = -1
        self.lock_db = lock_db
        self.event_graph = event_graph
        self.monederos = [Monedero(dinero_inicial / 2), Monedero(dinero_inicial / 2)]
        self.start_time_regression_medium = datetime(2020, 1, 1)

    @property
    def dinero(self):
        return self.__dinero

    @dinero.setter
    def dinero(self, valor):
        if valor < -0.0001:
            raise ExcepcionNoSePuedeComprar(f"No se puede tener dinero negativo {valor}")
        elif valor < 0:
            valor = 0
        self.__dinero = valor       

        self.refresh_dinero_total()

    @property
    def crypto(self):
        return self.__crypto

    @crypto.setter
    def crypto(self, valor):
        if valor < -0.0001:
            raise ExcepcionNoSePuedeComprar(f"No se puede tener crypto negativo{valor}")
        elif valor < 0:
            valor = 0

        self.__crypto = valor
        self.refresh_dinero_total()
    

    def refresh_dinero_total(self, precio=0):
        self.refresh_db()
        if precio == 0:
            precio  = self.df.iloc[-1,].Price
        self.dinero_total = self.dinero + self.crypto * precio



    def refresh_db (self):
        if self.lock_db == None:
            self.df = pd.read_csv("{}.csv".format(self.moneda))
        else:
            with self.lock_db:
                self.df = pd.read_csv("{}.csv".format(self.moneda))
        self.date_2_datetime()

    def date_2_datetime(self):
        self.df.Date = pd.to_datetime(self.df.Date)

    def min_day(self):
        day_date = datetime.now() - timedelta(days=1)

        year = day_date.year
        month = day_date.month
        day = day_date.day

        i_min = self.df.loc[self.df.Date >= datetime(year, month, day)]["Price"].idxmin()
        return self.df.iloc[i_min,].Price

    def max_day(self):
        day_date = datetime.now().date() - timedelta(days=1)
        year = day_date.year
        month = day_date.month
        day = day_date.day

        i_max = self.df.loc[self.df.Date >= datetime(year, month, day)]["Price"].idxmax()
        return self.df.iloc[i_max,].Price

    def min_to_date(self, dates):
        try:
            if not type(dates) == list:
                dates = [dates, datetime.now()]

            i_min = self.df.loc[(dates[1] >= self.df["Date"]) & (self.df["Date"] >= dates[0])]["Price"].idxmin()
            return self.df.iloc[i_min,].Price
        except Exception as e:
            return e
       
    def max_to_date(self, dates):
        try:
            if not type(dates) == list:
                dates = [dates, datetime.now()]

            i_max = self.df.loc[(dates[1] >= self.df["Date"]) & (self.df["Date"] >= dates[0])]["Price"].idxmax()
            return self.df.iloc[i_max,].Price
        except Exception as e:
            return e

    def mean_day(self):
        day_date = datetime.now().date() - timedelta(days=1)
        year = day_date.year
        month = day_date.month
        day = day_date.day

        return self.df.loc[self.df.Date >= datetime(year, month, day)]["Price"].mean()

    def mean_to_date(self, dates):
        try:
            if not type(dates) == list:
                dates = [dates, datetime.now()]
            return self.df.loc[(dates[1] >= self.df["Date"]) & (self.df["Date"] >= dates[0])]["Price"].mean()

        except Exception as e:
            return e

    def median_day(self):
        day_date = datetime.now().date() - timedelta(days=1)
        year = day_date.year
        month = day_date.month
        day = day_date.day

        return self.df.loc[self.df.Date >= datetime(year, month, day)]["Price"].median()

    def median_to_date(self, dates):
        try:
            if not type(dates) == list:
                dates = [dates, datetime.now()]
            return self.df.loc[(dates[1] >= self.df["Date"]) & (self.df["Date"] >= dates[0])]["Price"].median()

        except Exception as e:
            return e

    def std_day(self):
        day_date = datetime.now().date() - timedelta(days=1)
        year = day_date.year
        month = day_date.month
        day = day_date.day

        return self.df.loc[self.df.Date >= datetime(year, month, day)]["Price"].std()

    def std_to_date(self, dates):
        try:
            if not type(dates) == list:
                dates = [dates, datetime.now()]
            return self.df.loc[(dates[1] >= self.df["Date"]) & (self.df["Date"] >= dates[0])]["Price"].std()

        except Exception as e:
            return e


    def prepare_graph(self, dates):
        if not type(dates) == list:
            dates = [dates, datetime.now()]

        plt.style.use("default")
        self.refresh_db()

        #transformar a matplot los dias pero solo los del rango
        mdate_serie = date2num(self.df.loc[(dates[1] >= self.df["Date"]) & (self.df["Date"] >= dates[0])]["Date"])
        price_serie = self.df.loc[(dates[1] >= self.df["Date"]) & (self.df["Date"] >= dates[0])]["Price"]


        plt.plot(mdate_serie, price_serie, color="mediumblue", marker='', linestyle="-", linewidth=0.5, markersize=0.75)


        #valor minimo
        min_value = round(self.min_to_date(dates), 1)
        plt.axhline(y = min_value, label=("Min: " + str(min_value)), color="r", linestyle="--", linewidth=0.8)
        #valor maximo
        max_value = round(self.max_to_date(dates), 1)
        plt.axhline(y = max_value, label=("Max: " + str(max_value)), color="g", linestyle="--", linewidth=0.8)
        #promedio
        mean = round(self.mean_to_date(dates), 1)
        plt.axhline(y = mean, label=("Mean: " + str(mean)), color="b", linestyle="--", linewidth=0.8)
        #std
        std = round(self.std_to_date(dates) ,2)
        plt.axhline(y = mean + std,  color="darkorange", linestyle="--", linewidth=1)
        plt.axhline(y = mean - std,  color="darkorange", linestyle="--", linewidth=1)

        #fee
        fee = round(mean * cte_fee ,2)
        plt.axhline(y = mean + fee,  color="cyan", linestyle="--", linewidth=1)
        plt.axhline(y = mean - fee,  color="cyan", linestyle="--", linewidth=1)






        #rango en eje x
        plt.xlim(dates)

        #nos entrega los ejes
        ax = plt.gca()

        #setear el visualizador del eje x
        if dates[1] - dates[0] <= timedelta(hours=1):
            ax.xaxis.set_major_locator(MinuteLocator(byminute=(0, 15, 30, 45)))
        elif dates[1] - dates[0] <= timedelta(hours=3):
            ax.xaxis.set_major_locator(HourLocator(byhour=(0, 1, 2)))
        elif dates[1] - dates[0] <= timedelta(hours=6):
            ax.xaxis.set_major_locator(HourLocator(byhour=(0, 2, 4)))
        elif dates[1] - dates[0] <= timedelta(hours=12):
            ax.xaxis.set_major_locator(HourLocator(byhour=(0, 3, 6, 9)))
        elif dates[1] - dates[0] <= timedelta(hours=24):
            ax.xaxis.set_major_locator(HourLocator(byhour=(0, 6, 12, 18)))
        elif dates[1] - dates[0] <= timedelta(days=4):
            ax.xaxis.set_major_locator(HourLocator(byhour=(0, 12)))
        elif dates[1] - dates[0] <= timedelta(days=7):
            ax.xaxis.set_major_locator(DayLocator(bymonthday=(0, 2, 4, 6)))
        elif dates[1] - dates[0] <= timedelta(days=31):
            ax.xaxis.set_major_locator(DayLocator(byhour=(0, 7, 14, 21, 28)))
        else:
            ax.xaxis.set_major_locator(MontLocator())

        #Nombres a los ejes
        plt.xlabel('Fechas')    
        plt.ylabel('Precio en USD $')
    
        #Poner titulo
        plt.title("{}".format(self.moneda.upper()))

        #Que tenga un grid
        plt.grid(True)


    def show_graph(self):
        
        #legends
        fig = plt.gcf()
        fig.legend(loc=1)
        #fig.legend(loc="best")
        fig.tight_layout()
        #plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")

        plt.show()

    def dates_in_range(self, dates):
        if not type(dates) == list:
            dates = [dates, datetime.now()]
        
        return self.df.loc[(dates[1] >= self.df["Date"]) & (self.df["Date"] >= dates[0])]["Date"]
        



    def moving_average_hours(self, actual_date=None,hours=10):
        self.refresh_db()
        if not type(actual_date) == datetime.datetime:
            actual_date = datetime.now()

        date_begin = actual_date - timedelta(hours = hours)
        serie_date = self.dates_in_range([date_begin, actual_date])

        return serie_date.mean()




    def comprar_monedas(self, cantidad_usd = -1, precio=0):
        #cantidad un float
        self.refresh_db()
        if precio == 0:
            precio  = self.df.iloc[-1,].Price
        
        if cantidad_usd == -1:
            cantidad_usd = self.dinero

        
        self.dinero -= cantidad_usd

        cantidad_usd_con_interes = cantidad_usd - cantidad_usd * cte_fee

        cantidad_crypto = cantidad_usd_con_interes / precio
        self.crypto += cantidad_crypto
        self.refresh_dinero_total(precio)

        print(f"Vendiste\tUSD: {cantidad_usd}\t\tCompraste\tcrypto: {cantidad_crypto}\t\tDinero total: {self.dinero_total}")


        with open(f"{venta_compra}.txt", "a", encoding="utf-8") as archive:
            archive.write(f"Vendiste\tUSD: {cantidad_usd}\t\tCompraste\tcrypto: {cantidad_crypto}\t\tDinero total: {self.dinero_total}\n\n")




    def vender_monedas(self, cantidad_usd=-1, cantidad_crypto= -1, precio=0):
        #cantidad un float
        self.refresh_db()
        if precio == 0:
            precio  = self.df.iloc[-1,].Price

        if cantidad_usd == -1 and cantidad_crypto == -1:
            cantidad_crypto = self.crypto
            self.crypto -= cantidad_crypto
            cantidad_crypto_con_interes = cantidad_crypto - cantidad_crypto * cte_fee
            cantidad_usd_con_interes = cantidad_crypto_con_interes * precio


        elif cantidad_crypto == -1:
            cantidad_crypto = cantidad_usd / precio    
            self.crypto -= cantidad_crypto
            cantidad_crypto_con_interes = cantidad_crypto - cantidad_crypto * cte_fee
            cantidad_usd_con_interes = cantidad_usd - cantidad_usd * cte_fee

        else:
            self.crypto -= cantidad_crypto
            cantidad_crypto_con_interes = cantidad_crypto - cantidad_crypto * cte_fee
            cantidad_usd_con_interes = cantidad_crypto_con_interes * precio


        self.dinero += cantidad_usd_con_interes
        self.refresh_dinero_total(precio)
        print(f"Compraste\tUSD: {cantidad_usd_con_interes}\t\tVendiste\tcrypto: {cantidad_crypto}\t\tDinero total: {self.dinero_total}")
        with open(f"{venta_compra}.txt", "a", encoding="utf-8") as archive:
            archive.write(f"Compraste\tUSD: {cantidad_usd_con_interes}\t\tVendiste\tcrypto: {cantidad_crypto}\t\tDinero total: {self.dinero_total}\n\n")

    
    def prediction_OLS (self, dates, degree):
        #retorna los resultados de la regression

        self.refresh_db()

        if not type(dates) == list:
            dates = [dates, datetime.now()]

        #fechas que se van a usar
        date_series = self.df.loc[(dates[1] >= self.df["Date"]) & (self.df["Date"] >= dates[0])]["Date"]

        #hay que pasar las fechas a julian date para que sea pasable por la regresion
        date_float_series = date_series.map(pd.Timestamp.to_julian_date)
        
        #reescalar
        date_float_series -= date_float_series.iloc[0]
        date_float_series *= cte_amplificador_regression
        
        #tiene que estar en numpy, todos los datos en la misma columna
        x = date_float_series.to_numpy().reshape(-1,1)
        
        #La data que se le mete al modelo
        #si queremos ordenes superiores, hay que añadir columnas con el
        #x elevado según el grado que se quiera añadir

        polynomial_features= PolynomialFeatures(degree=degree)
        X = polynomial_features.fit_transform(x)

        Y = self.df.loc[(dates[1] >= self.df["Date"]) & (self.df["Date"] >= dates[0])]["Price"]

        #queremos obtener el intercepto, por lo que se le añade una columna de 1s
        X = sm.add_constant(X)

        #hacemos el fit en ordinary least squares
        model = sm.OLS(Y, X)
        results = model.fit()
        return results


    def prediction_OLS_graph (self, dates, degree):
        self.refresh_db()

        if not type(dates) == list:
            dates = [dates, datetime.now()]

        plt.style.use("default")

        #fechas que se van a usar
        date_series = self.df.loc[(dates[1] >= self.df["Date"]) & (self.df["Date"] >= dates[0])]["Date"]
        mdate_series = date2num(date_series)

        #hay que pasar las fechas a julian date para que sea pasable por la regresion
        date_float_series = date_series.map(pd.Timestamp.to_julian_date)
        
        #reescalar
        date_float_series -= date_float_series.iloc[0]
        date_float_series *= cte_amplificador_regression
        
        #tiene que estar en numpy, todos los datos en la misma columna
        x = date_float_series.to_numpy().reshape(-1,1)
        
        #La data que se le mete al modelo
        #si queremos ordenes superiores, hay que añadir columnas con el
        #x elevado según el grado que se quiera añadir

        polynomial_features= PolynomialFeatures(degree=degree)
        X = polynomial_features.fit_transform(x)

        Y = self.df.loc[(dates[1] >= self.df["Date"]) & (self.df["Date"] >= dates[0])]["Price"]

        #queremos obtener el intercepto, por lo que se le añade una columna de 1s
        X = sm.add_constant(X)

        #hacemos el fit en ordinary least squares
        model = sm.OLS(Y, X)
        results = model.fit()

        #R squared
        #print(f"R2:\t\t{results.rsquared}")

        #prediction_interval = prediction_interval.conf_int(alpha=0.05)
                
        ax = plt.gca()
        ax.plot(mdate_series, results.predict(),  color='red', marker='', linestyle='dashed', linewidth=0.75, markersize=1)
        
        #Prediccion

        """prediction_ols = results.get_prediction()
        iv_l = prediction_ols.summary_frame()["obs_ci_lower"]
        iv_u = prediction_ols.summary_frame()["obs_ci_upper"]
        ax.plot(mdate_series, iv_u, "r--")
        ax.plot(mdate_series, iv_l, "r--")"""


        """from statsmodels.sandbox.regression.predstd import wls_prediction_std
        _, upper,lower = wls_prediction_std(model)

        plt.scatter(x,y)
        plt.plot(x,ypred)
        plt.plot(x,upper,'--',label="Upper") # confid. intrvl
        plt.plot(x,lower,':',label="lower")
        plt.legend(loc='upper left')"""




    def modelo_simple_1(self, dates=-1):
        #date es una desde el pasado


        """#in hours
        time_regression_medium = 6
        #in hours
        time_average = 6
        #in hours
        time_std = 9
        #en minutos
        time_regression_smallest = 30
        #en minutos
        time_regression_smallest_2 = time_regression_smallest * 0.3"""

        self.refresh_db()

        if dates == -1:
            date_0 = datetime(2021, 12, 24)
            date_1 = pd.to_datetime(self.df.iloc[-1].Date)
            dates = [date_0, date_1]

        elif not type(dates) == list:
            dates = [dates, datetime.now()]

        last_price = self.df["Price"].iloc[-1]

        #------------------pendiente de linea de tiempo corto--------------------------------------------------------
        result_smallest = self.prediction_OLS([dates[1] - timedelta(minutes=time_regression_smallest), dates[1]], 1)
        #print(f"R2:\t{result_smallest.rsquared}")
        #print(f"Params:\n{result_smallest.params}")
        #print(f"Slope:\t{result_smallest.params[1]}")
        slope_smallest = result_smallest.params[1]
        


        #print(f"Smallest: {str_slope_smallest}")
        #print()


        #-----------------------Curva de tiempo corto--------------------------------------------------------------
        result_small_curve = self.prediction_OLS([dates[1] - timedelta(minutes=time_regression_smallest_2), dates[1]], 2)
        curve_small = result_small_curve.params[2]
        #print(f"R2 medium:\t{result_medium.rsquared}")
        #print(f"Params:\n{result_medium.params}")



        #----------------------Pendiente de tiempo mediano
        """if dates[1] - timedelta(hours=time_regression_medium) > self.start_time_regression_medium:
            result_medium_regression = self.prediction_OLS([dates[1] - timedelta(hours=time_regression_medium), dates[1]], 1)
        else:
            result_medium_regression = self.prediction_OLS([self.start_time_regression_medium, dates[1]], 1)"""
        result_medium_regression = self.prediction_OLS([dates[1] - timedelta(hours=time_regression_medium), dates[1]], 1)
        slope_medium = result_medium_regression.params[1]
        result_medium_last_value = result_medium_regression.predict()[-1]
        




        average = self.mean_to_date([dates[1] - timedelta(hours=time_average), dates[1]])
        average_fee = average * cte_fee
        std = self.std_to_date([dates[1] - timedelta(hours=time_std), dates[1]])

        


        # ------------------------- Logica del modelo -------------------------------------------
        
        def logica (self, monedero):
            # --------------- Modo obtener low threashold ------------------------

            low_threshold_list = []
            if modo_obtener_low_threshold == "regression":

                result_medium_last_value_fee = result_medium_last_value * cte_fee
                low_threshold_list.append(result_medium_last_value - result_medium_last_value_fee * cte_low_threshold)

            elif modo_obtener_low_threshold == "average":

                low_threshold_list.append(average - average_fee * cte_low_threshold)

            for i in range(len(self.monederos)):
                if self.monederos[i].have_crypto:
                    low_threshold_list.append(self.monederos[i].last_bought_price - self.monederos[i].last_bought_price * cte_fee * cte_low_threshold_2)

                monedero.low_threshold = min(low_threshold_list)


            #----------------- Modo obtener high threshold -------------------------

            if modo_obtener_low_threshold == "regression":
                monedero.set_high_threshold(average=average, average_fee=average_fee, result_medium_last_value_fee=result_medium_last_value_fee, result_medium_last_value = result_medium_last_value)
            elif modo_obtener_low_threshold == "average":
                monedero.set_high_threshold(average=average, average_fee=average_fee)
                



            if 0 < slope_smallest:

                if curve_small > curva_threshold: 

                    """#se sigue con la logica  
                    if not self.last_sell_price_downfall == -1:        
                        if self.last_sell_price_downfall - self.last_sell_price_downfall * cte_fee * cte_low_threshold > last_price:
                            if monedero.low_threshold > last_price and std > average_fee:

                                if not monedero.have_crypto:
                                    
                                    monedero.last_bought_price = last_price
                                    monedero.have_crypto = True
                                    monedero.comprar_vender = True
                                    self.last_sell_price_downfall = -1
                                    self.start_time_regression_medium = dates[1]

                                    return  'Comprar'"""

                    #else:

                    print("monedero low threashold:", monedero.low_threshold)
                    if monedero.low_threshold > last_price:

                        if std > average_fee:


                            if not monedero.have_crypto:
                                
                                monedero.last_bought_price = last_price
                                monedero.have_crypto = True
                                monedero.comprar_vender = True

                                return  "Comprar"

            
            elif 0 > slope_smallest:

                if curve_small < -1 * curva_threshold:

                    if monedero.high_threshold < last_price:

                        if monedero.have_crypto:
                            monedero.have_crypto = False
                            monedero.comprar_vender = True
                            return 'Vender'

                    """elif last_price < monedero.last_bought_price - monedero.last_bought_price * cte_fee * cte_last_bought_price:
                        if monedero.have_crypto:
                            monedero.have_crypto = False
                            monedero.comprar_vender = True
                            self.last_sell_price_downfall = last_price
                            return 'Vender'"""

            return "Nada"

        
        for monedero in self.monederos:
            accion = logica(self, monedero)    
                
            if not accion == "Nada":
                with open(f"{venta_compra}.txt", "a", encoding="utf-8") as archive:
                    archive.write(f"Accion,{accion}\n")
                    archive.write(f"Fecha,{dates[1]}\n")
                    archive.write(f"Last Price,{last_price}\n")
                    if modo_obtener_low_threshold == "regression":
                        archive.write(f"Regression medium slope:{slope_medium} last value:{result_medium_last_value}\n")
                    elif modo_obtener_low_threshold == "average":
                        archive.write(f"Average value: {average}\n")
                    archive.write(f"Slope value: {slope_smallest}\n")
                    archive.write(f"Curve value: {curve_small}\n")

                if accion == "Comprar":

                    if monedero.comprar_vender == True:
                        precio = self.df.iloc[-1,].Price
                        self.comprar_monedas(cantidad_usd=monedero.dinero, precio = precio)
                        monedero.comprar_monedas(precio= precio)
                        monedero.comprar_vender = False
                            
                            
                elif accion == "Vender":

                    if monedero.comprar_vender == True:
                        price = self.df.iloc[-1,].Price
                        self.vender_monedas(cantidad_crypto=monedero.crypto, precio = price)
                        monedero.vender_monedas(precio = price)
                        monedero.comprar_vender = False
                        


            dic_enviar = {
                "average" : average,
                "std" : std,
                "min" : round(self.min_to_date(dates), 2),
                "max" : round(self.max_to_date(dates), 2),
                "low_threshold" : monedero.low_threshold,
                "high_threshold" : monedero.high_threshold,
                "slope" : slope_smallest,
                "curve" : curve_small,
                "date_0" : str(dates[0]),
                "date_1" : str(dates[1]),
                "result_medium_last_value" : result_medium_last_value,
            }

            print(f"Fecha:\t\t{dates[1]}")
            print(f"Last Price:\t{last_price}")
            print(f"Slope:\t\t{slope_smallest}")
            print(f"curve:\t\t{curve_small}\n")

            with open("graph_data.json", "w", encoding="utf-8") as archive:
                json.dump(dic_enviar, archive)
       

                














        







        






if __name__ == "__main__":
    bitcoin = Calculadora("Bitcoin-USD")
    bitcoin.refresh_db()
    bitcoin.date_2_datetime()
    print(bitcoin.min_day())
    print(bitcoin.max_day())
    print(bitcoin.min_to_date(22))
    print(bitcoin.max_to_date(datetime(2021, 12, 21, 0)))
    print(bitcoin.min_to_date(datetime(2021, 12, 21, 0)))
    print("average:", bitcoin.mean_day())
    print("median:", bitcoin.median_day())
    print("desviacion estandar:", bitcoin.std_day())
    
    inicial = 100
    bitcoin.dinero = inicial
    bitcoin.comprar_monedas(100, precio = 50486)
    bitcoin.vender_monedas()
    print(f"Porcentaje ganancia:\t{(bitcoin.dinero - inicial) / inicial * 100}")

    range_days_1 = [datetime(2021,12,26,0), datetime(2021, 12, 26, 13, 7)]
    print()
    print(bitcoin.prediction_OLS(datetime(2021, 12, 26), 2).rsquared)

    range_days_1 = [datetime(2021,12,26,0), datetime.now()]
    bitcoin.prepare_graph(range_days_1)

    minutos = 30
    for i in range(15):
        range_days_2 = [range_days_1[1] - timedelta(minutes= minutos + i * minutos), range_days_1[1] - timedelta(minutes=i * minutos) ]
        bitcoin.prediction_OLS_graph(range_days_2, 1)

    bitcoin.prediction_OLS_graph([range_days_1[0], range_days_1[1]], 1)
    
    bitcoin.show_graph()

    print("\n")
    bitcoin.modelo_simple_1(range_days_1)



