#how to use basic Alpha Vantage -> https://github.com/RomelTorres/alpha_vantage
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.cryptocurrencies import CryptoCurrencies
import pandas as pd
import matplotlib.pyplot as plt
from googlefinance.get import get_data
from datetime import datetime
import sys
from pandas_datareader import data as pdr
import pandas_datareader
from datetime import timedelta

class Buisy :
    def __init__(self) :
        self.auth = "__alpha_vantage_api_key" #authentic key alpha vantage api

        self.ts =  TimeSeries(key=self.auth, output_format='pandas') #instance alpha vantage api

    def getStock(self, keyword, since=None, until=None ) :
        ### get tuple with pair of (data, metadata) with input keyword of stock

        self.isValidSinceUntil(since, until)  #check for since and until is correct
        if (since != None and until != None ) :
            #calculate if since and date is a liitle of different
            d1 = datetime.strptime(since, "%Y-%m-%d") #convert since  to datetime object
            d2 = datetime.strptime(until, "%Y-%m-%d") #convert until to datetime object
            diff_days = abs((d2 - d1).days) #find different of since and until
            if diff_days <= 5 :
                since = (d2-timedelta(days=10)).strftime("%Y-%m-%d") #set new range if since, until diff is only 5

        try :
            cc = CryptoCurrencies(key=self.auth , output_format='pandas') #instance cypto alpha vantage api
            data, meta_data = cc.get_digital_currency_daily(symbol=keyword, market='USD') #get inserted keyword data
            data = data[until:since]  #select since and until range
            return  data, meta_data #return data and metadata
        except ValueError :
            #if not found in cryptocurrencies
            try :
                data, meta_data = self.ts.get_intraday(symbol=keyword, outputsize='full', interval='1min') #find in stock
                data = data[until:since] #select since and until range
                return data, meta_data #return data and metadata
            except ValueError :
                try :
                    ptt = pdr.get_data_yahoo("{}.BK".format(keyword), start=since, end=until) #find stock name in yahoo stock data (SET STOCK)
                    ptt = ptt[::-1] #reverse data
                    return ptt,None #return data and None
                except pandas_datareader._utils.RemoteDataError :
                    #if not found any stock match
                    raise Exception("Invalid Stock Name")

    def isValidSinceUntil(self, since, until) :
        if  (since!=None and until!=None) :
            d1 = datetime.strptime(since, "%Y-%m-%d") #convert since to datetime object
            d2 = datetime.strptime(until, "%Y-%m-%d")  #convert until to datetime object
            if (d2-d1).days <= 0 :
                raise Exception("Insert Again Since is new than Until") #if it's negative day (since less more than until)
            else :
                return True #return true if collect
        else :
            return True #return true if collect



if __name__ == "__main__" :
    app = Buisy()
    print(type(app.getStock("DOGE")))
