import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import json
import statsmodels.api as sm
from datetime import datetime, timedelta
from matplotlib.dates import date2num, HourLocator, MinuteLocator, DayLocator, MonthLocator
from sklearn.preprocessing import PolynomialFeatures

import parametros
from classes import *
from functions import *



class Oscilations:
    def __init__(self, info_base):
        pass