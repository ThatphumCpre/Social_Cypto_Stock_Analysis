

# Form implementation generated from reading ui file 'ui_trendy.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QDateTime
from PyQt5.QtCore import QDate
from webCrawler  import WebCrawler
from twitterCrawler import Trendy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
from PyQt5.QtWidgets import*
from matplotlib.backends.backend_qt5agg import FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from biTools import Buisy
import pandas as pd
import io
import threading
import concurrent.futures
import time
import plotly.graph_objs as go
from functools import partial
import plotly
from datetime import datetime
import re
from datetime import timedelta

class MplTrendtags(QWidget):

    def __init__(self, parent = None):

        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(plt.figure(figsize=(4, 3)))
        try:
            plt.rcParams['font.family'] = 'TH SarabunPSK'
        except:
            plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['font.size'] = 12

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.subplots()
        self.setLayout(vertical_layout)

class MplPoptrend(QWidget):

    def __init__(self, parent = None):

        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(plt.figure())
        plt.rcParams['font.family'] = 'TH SarabunPSK'
        plt.rcParams['font.size'] = 16

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.setLayout(vertical_layout)

class Worker_TrendWord(QObject) :

    finished = pyqtSignal()
    returned = pyqtSignal(object)
    temp = pyqtSignal(int)

    def __init__(self) :
        super().__init__()

    def run(self,objTwitter,keyword,since,until,window,test) :
        print(":::::::DSADASDASD::::::", keyword)
        keyword = keyword.replace("#","")
        data = objTwitter.findAndCombineTrend(keyword, since=since, until=until, test=test)
        window.plotTrendWord(data)
        self.returned.emit(data)
        self.finished.emit()

class Worker_datecheck(QObject) :

    finished = pyqtSignal()

    def __init__(self) :
        super().__init__()

    def run(self,objTwitter,keyword,since,until,window) :
        data = objTwitter.datecheck(keyword, since, until)
        self.finished.emit()

class Worker_GraphStock(QObject) :

    finished = pyqtSignal()
    returned = pyqtSignal(object)

    def __init__(self) :
        super().__init__()

    def run(self, stock_name, since, until, window, stockTools) :
        start = time.time()
        data, meta_data = stockTools.getStock(stock_name,since=since, until=until)

        start = time.time()
        fig = go.Figure()
        print("===========================================1", time.time()-start)
        try :
            print("===========================================2", time.time()-start)
            fig.add_trace(go.Candlestick(x=data.index[:10],
                                        open=data['Open'],
                                        high = data['High'],
                                        low=data['Low'],
                                        close=data['Close'],
                                        name = 'market data'))
            dates = data.index.strftime('%Y-%m-%d').tolist()


        except KeyError :
            try :
                print("===========================================2", time.time()-start)
                fig.add_trace(go.Candlestick(x=data.index[:10],
                                            open=data['1. open'],
                                            high = data['2. high'],
                                            low=data['3. low'],
                                            close=data['4. close'],
                                            name = 'market data'))
                dates = data.index.strftime('%Y-%m-%d').tolist()


            except KeyError :
                print("===========================================2", time.time()-start)
                fig.add_trace(go.Candlestick(x=data.index[:10],
                                            open=data['1a. open (USD)'],
                                            high = data['2a. high (USD)'],
                                            low=data['3a. low (USD)'],
                                            close=data['4a. close (USD)'],
                                            name = 'market data'))
                dates = data.index.strftime('%Y-%m-%d').tolist()


        print("===========================================2", time.time()-start)
        excludeDate = list()
        first = datetime.strptime(dates[-1], "%Y-%m-%d")
        last = datetime.strptime(dates[0], "%Y-%m-%d")
        while (first < last ) :
            if first.strftime('%Y-%m-%d') not in dates :
                excludeDate.append(first.strftime('%Y-%m-%d')) #dedete date show that exclude
            first = first+timedelta(days=1)
            print(first)
        print("===========================================3", time.time()-start)

        #dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(data.index)]
        #dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in data]
        fig.update_xaxes(rangebreaks=[dict(values=excludeDate)])
        fig.update_layout(yaxis_title='Stock price (USE per Shares)',width=500, height=400, xaxis_rangeslider_visible=False)
        print("===========================================4", time.time()-start)
        #fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

        #convert to html code
        raw_html = '<html><head><meta charset="utf-8" />'
        raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_html += '<body>'
        raw_html += plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
        raw_html += '</body></html>'

        print("===========================================4", time.time()-start)

        self.returned.emit(raw_html) #emit raw html to update to ui
        #window.plotStockData(data_Stonk)
        self.finished.emit()




class Worker_Sentiment(QObject) :

    finished = pyqtSignal()
    returned = pyqtSignal(object)
    progress = pyqtSignal(int)

    def __init__(self) :
        super().__init__()

    def run(self,objTwitter,keyword,since,until,window, worker) :
        data = objTwitter.findAndCombineSentiment( keyword, since=since, until=until, worker=worker)
        self.returned.emit(data)
        self.finished.emit()


class Worker_heatmap(QObject) :

    finished = pyqtSignal()
    returned = pyqtSignal(object)
    progress = pyqtSignal(int)

    def __init__(self) :
        super().__init__()

    def run(self,objTwitter,keyword,since,until,window, worker) :
        print("::::::::",self)
        start = time.time()
        data = objTwitter.geopyToPandas( keyword, since=since, until=until, worker=worker)
        self.progress.emit(100)
        self.returned.emit(data)
        self.finished.emit()
        print("estimate", time.time()-start)

class Worker_SentimentWeb(QObject) :

    finished = pyqtSignal()
    returned = pyqtSignal(object)
    progress = pyqtSignal(int)

    def __init__(self) :
        super().__init__()

    def run(self,objWebcrawl,keyword,since,until,window,worker) :
        future = objWebcrawl.sentimentWeb( keyword, since=since, until=until, worker=worker)
        self.returned.emit(future)
        self.finished.emit()

class Worker_TrendWordWeb(QObject) :

    finished = pyqtSignal()
    returned = pyqtSignal(object)
    temp = pyqtSignal(int)

    def __init__(self) :
        super().__init__()

    def run(self,objWebcrawl,keyword,since,until,window,worker) :
        data = objWebcrawl.analyze(keyword, since, until, plot=False, worker=worker)
        self.returned.emit(data)
        self.finished.emit()


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 850)
        MainWindow.setStyleSheet("background-color: rgb(253,253,255);")
        self.waitingThread = 0
        self.doneThread = 0
        self.windowObject = MainWindow
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.webCrawler = WebCrawler()
        self.badLocation = [":","/","#","@","?",'&', ';', "…", "^","♡","♪","･","!","♥"]
        self.emoji_pattern = re.compile("["
                                    u"\U0001F600-\U0001F64F"  # emoticons
                                    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                    u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                    "]+", flags=re.UNICODE)


        self.twitterCrawler = Trendy(pBar=self)
        self.stonk = Buisy()




        self.dateEdit = QtWidgets.QDateEdit(self.centralwidget)
        self.dateEdit.setGeometry(QtCore.QRect(140, 280, 121, 51))


        self.dateEdit.setObjectName("dateEdit")
        self.dateEdit_2 = QtWidgets.QDateEdit(self.centralwidget)
        self.dateEdit_2.setGeometry(QtCore.QRect(410, 280, 121, 51))
        self.dateEdit_2.setObjectName("dateEdit_2")

        current_dateTime = datetime.now()
        d = QDateTime(current_dateTime.year, current_dateTime.month, current_dateTime.day, 10, 30)
        self.dateEdit.setMaximumDateTime(d)
        self.dateEdit_2.setMaximumDateTime(d)
        self.dateEdit.setDate(QDate.currentDate())
        self.dateEdit_2.setDate(QDate.currentDate())


        self.currentTime = QDate.currentDate().toString("yyyy-MM-dd")


        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(120, 10, 341, 171))
        self.label.setStyleSheet("font: 50pt \"Sukhumvit Set\";")
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(50, 220, 521, 51))
        self.lineEdit.setStyleSheet("background-color : rgb(255, 255, 255);\n"
                                    "font: 22pt \"TH SarabunPSK\";")
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.placeholderText()
        self.lineEdit.setPlaceholderText("Insert Keyword that you want here.")
        self.listView = QtWidgets.QListView(self.centralwidget)
        self.listView.setGeometry(QtCore.QRect(110, 420, 371, 411))
        self.listView.setObjectName("listView")
        self.listView.setStyleSheet("background-color : rgb(255, 255, 255);\n"
                                    "font: 18pt \"TH SarabunPSK\";")
        print("hi")

        model = QtGui.QStandardItemModel()
        self.listView.setModel(model)
        for i in self.twitterCrawler.viewTrends():
            item = QtGui.QStandardItem(i)
            model.appendRow(item)
        self.listView.setObjectName("listView")
        self.listView.clicked.connect(self.selectItem)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(50, 350, 391, 61))
        self.pushButton.setStyleSheet("background-color : rgb(127, 166, 255);\n"
                                        "font: 75 24pt \"TH SarabunPSK\";\n"
                                        "border : none; \n"
                                        "padding-top: 5px;\n"
                                        "color : rgb(249, 255, 255);\n"
                                        "border-radius : 10px;")
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(450, 350, 121, 61))
        self.pushButton_2.setStyleSheet("background-color : rgb(127, 166, 255);\n"
                                        "font: 75 24pt \"TH SarabunPSK\";\n"
                                        "border : none; \n"
                                        "padding-top: 5px;\n"
                                        "color : rgb(249, 255, 255);\n"
                                        "border-radius : 10px;")
        self.pushButton_2.setObjectName("pushButton_2")
        #self.pushButton_2.clicked.connect( lambda x:self.webButton(MainWindow))
        #self.pushButton.clicked.connect(lambda x:self.twitBuntton(MainWindow))
        self.pushButton.clicked.connect(self.runLongTask)
        self.pushButton_2.clicked.connect(self.webButton)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(60, 300, 60, 16))
        self.label_2.setStyleSheet("font: 75 24pt \"TH SarabunPSK\";")
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(320, 300, 60, 16))
        self.label_3.setStyleSheet("font: 75 24pt \"TH SarabunPSK\";")
        self.label_3.setObjectName("label_3")
        self.widget_showgraph = MplPoptrend(self.centralwidget)

        self.widget_showgraph2 = MplTrendtags(self.centralwidget)

        self.widget_showgraph3 = QtWebEngineWidgets.QWebEngineView(self.centralwidget)


        self.view = QtWebEngineWidgets.QWebEngineView(self.centralwidget)



        self.widget_showgraph.setGeometry(QtCore.QRect(600, 0, 0, 0))
        self.widget_showgraph2.setGeometry(QtCore.QRect(1100, 0, 0 , 0))
        self.widget_showgraph3.setGeometry(QtCore.QRect(600, 440, 0, 0))
        self.view.setGeometry(QtCore.QRect(1110, 450, 0, 0))

        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(1150, 100, 400, 300))
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)

        self.progressBarHeat = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBarHeat.setGeometry(QtCore.QRect(1150, 500, 400, 300))
        self.progressBarHeat.setValue(0)
        self.progressBarHeat.setVisible(False)

        self.progressBarSentiment = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBarSentiment.setGeometry(QtCore.QRect(650, 100, 400, 300))
        self.progressBarSentiment.setValue(0)
        self.progressBarSentiment.setVisible(False)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)




    def plotTrend(self, data):
        label = data.keys()
        values = data.values()
        self.widget_showgraph.canvas.axes.clear()
        self.widget_showgraph.canvas.axes.set_title("Sentiment Analyzis")
        self.widget_showgraph.canvas.axes.pie(values, labels=label,
                                                autopct='%1.1f%%',
                                                startangle=10,colors=["lightgreen","lightgray","lightcoral"] )
        self.widget_showgraph.canvas.draw()

    def plotStockData(self, raw_html) :
        self.widget_showgraph3.setHtml(raw_html)


    def plotTrendWord(self, data, rankNo=5) :

        label = [] #empty label , values, explode
        values = []
        explode = []
        count = 0
        if( len(data) < 5) :
            rankNo = len(data)
        for k in data :
            count += k[1]
        for k in range(rankNo) :
            explode.append(0.1)
            label.append(data[k][0])  #add to label list
            values.append(data[k][1]/count*100) #calculate percent

        x = np.arange(0,rankNo)

        self.widget_showgraph2.canvas.axes.clear()
        self.widget_showgraph2.canvas.axes.set_title("TREND WORD IN TWEET")
        self.widget_showgraph2.canvas.axes.bar(label, values, color='slateblue')
        self.widget_showgraph2.canvas.draw()

    def plotTrendWordWeb(self, data, rankNo=5) :

        label = [] #empty label , values, explode
        values = []
        explode = []
        count = 0
        if( len(data) < 5) :
            rankNo = len(data)
        for k in data :
            count += k[1]
        for k in range(rankNo) :
            explode.append(0.1)
            temp = data[k][0].split("/")
            temp = temp[2].split(".")
            label.append(temp[1])  #add to label list
            values.append(data[k][1]/count*100) #calculate percent

        x = np.arange(0,rankNo)

        self.widget_showgraph2.canvas.axes.clear()
        self.widget_showgraph2.canvas.axes.set_title("TREND WORD IN TWEET")
        self.widget_showgraph2.canvas.axes.bar(label, values, color='slateblue')
        self.widget_showgraph2.canvas.draw()



    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "What\'s Trendy  ?"))
        self.pushButton.setText(_translate("MainWindow", "TWITTER ANALYZE"))
        self.pushButton_2.setText(_translate("MainWindow", "WEB"))
        self.label_2.setText(_translate("MainWindow", "SINCE :"))
        self.label_3.setText(_translate("MainWindow", "UNTIL"))

    def webButton(self, MainWindow) :

        self.windowObject.showMaximized()
        self.widget_showgraph.setGeometry(QtCore.QRect(600, 0, 500, 440))
        self.widget_showgraph2.setGeometry(QtCore.QRect(1100, 0, 500, 440))
        self.widget_showgraph3.setGeometry(QtCore.QRect(800, 440, 500, 440))
        self.view.setGeometry(QtCore.QRect(1110, 450, 0, 0))
        self.since = self.dateEdit.date().toString("yyyy-MM-dd")
        until_temp = self.dateEdit_2.date().toString("yyyy-MM-dd")
        dayTemp = datetime.strptime(until_temp, "%Y-%m-%d")
        dayTemp = dayTemp+timedelta(days=1)
        self.until = dayTemp.strftime("%Y-%m-%d")

        self.webThreadDo()
        #if (since == self.currentTime and until == self.currentTime) :
            #since = None
            #until = None
        #self.webCrawler.search("web", since=since, until=until)




    def runLongTask(self):
        #re-viewing all widget
        self.windowObject.showMaximized()
        self.widget_showgraph.setGeometry(QtCore.QRect(600, 0, 500, 440))
        self.widget_showgraph2.setGeometry(QtCore.QRect(1100, 0, 500, 440))
        self.widget_showgraph3.setGeometry(QtCore.QRect(600, 440, 500, 440))
        self.view.setGeometry(QtCore.QRect(1110, 450, 480, 420))

        #date since reading to attribute
        self.since = self.dateEdit.date().toString("yyyy-MM-dd")
        until_temp = self.dateEdit_2.date().toString("yyyy-MM-dd")
        dayTemp = datetime.strptime(until_temp, "%Y-%m-%d")
        dayTemp = dayTemp+timedelta(days=1)
        self.until = dayTemp.strftime("%Y-%m-%d")

        text = self.lineEdit.text()
        splited_text = text.split(":")
        if len(splited_text) >= 2  :
            self.text = splited_text[0].replace("#","")
            stock_name = splited_text[1]

        else :
            self.text = splited_text[0].replace("#","")

        #disable button
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)

        self.thread_0 = QThread()
        self.Worker_datecheck = Worker_datecheck()
        # Step 4: Move worker to the thread
        self.Worker_datecheck.moveToThread(self.thread_0)
        # Step 5: Connect signals and slots
        self.thread_0.started.connect(partial(self.Worker_datecheck.run, self.twitterCrawler,self.text , self.since , self.until , self))
        self.Worker_datecheck.finished.connect(self.thread_0.quit)
        self.Worker_datecheck.finished.connect(self.Worker_datecheck.deleteLater)
        self.thread_0.finished.connect(self.thread_0.deleteLater)
        #self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread_0.start()
        self.text = self.text.replace("#", "")
        self.thread_0.finished.connect(self.twitThreadDo) #if thread data checking done then do other thread

        #self.twitterCrawler.search(keyword=text, since=since, until=until)
    def webThreadDo(self) :

        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)

        text = self.lineEdit.text()
        splited_text = text.split(":")

        if (self.since == None and self.until == None ) :
            return 0
        elif (self.since != None and self.until == None ) :
            d1 = datetime.strptime(self.since, "%Y-%m-%d")
        elif (self.since == None and self.until != None ) :
            d2 = datetime.strptime(self.until, "%Y-%m-%d")
        else :
            d1 = datetime.strptime(self.since, "%Y-%m-%d")
            d2 = datetime.strptime(self.until, "%Y-%m-%d")
        dateList = list()
        i = 1
        diff_days = abs((d2 - d1).days)

        if (diff_days > 2 ) :
            self.trendThreadSize = 2
        else :
            self.trendThreadSize = 1
        self.waitingThread += self.trendThreadSize

        #calculate thread and divide conquere  from date
        for k in range(diff_days) :
            d3 = d1+timedelta(days=k)
            if (d3-d1).days > diff_days*i/self.trendThreadSize :
                break

        if len(splited_text) >= 2  :
            #if user input stock name
            self.text = splited_text[0].replace("#","")
            stock_name = splited_text[1]

            self.thread_3 = QThread()
            self.worker_graphStock = Worker_GraphStock()
            # Step 4: Move worker to the thread
            self.worker_graphStock.moveToThread(self.thread_3)
            # Step 5: Connect signals and slots
            self.thread_3.started.connect(partial(self.worker_graphStock.run, stock_name , self.since , self.until , self, self.stonk))
            self.worker_graphStock.finished.connect(self.thread_3.quit)
            self.worker_graphStock.finished.connect(self.worker_graphStock.deleteLater)
            self.thread_3.finished.connect(self.thread_3.deleteLater)
            self.worker_graphStock.returned.connect(self.plotStockData)
            self.thread_3.start()
            self.waitingThread += 1
            #self.worker.progress.connect(self.reportProgress)
            # Step 6: Start the thread


        else :


            self.text = text.replace("#","")

        if self.trendThreadSize == 2 :
            #do thread size = 2

            self.waitingThread += 4 #2*2 thread with sentiment and tokenized

            self.thread_2 = QThread()
            self.worker_sentiment = Worker_SentimentWeb()
            # Step 4: Move worker to the thread
            self.worker_sentiment.moveToThread(self.thread_2)
            # Step 5: Connect signals and slots
            self.thread_2.started.connect(partial(self.worker_sentiment.run, self.webCrawler, self.text , self.since , self.until , self, self.worker_sentiment))
            self.worker_sentiment.finished.connect(self.thread_2.quit)
            self.worker_sentiment.finished.connect(self.worker_sentiment.deleteLater)
            self.thread_2.finished.connect(self.thread_2.deleteLater)
            self.thread_2.finished.connect(self.jobDoneThread)
            self.worker_sentiment.progress.connect(self.updateProgressBarSentiment)
            self.worker_sentiment.returned.connect(self.plotTrend)

            self.thread_3 = QThread()
            self.worker_sentiment_2 = Worker_SentimentWeb()
            # Step 4: Move worker to the thread
            self.worker_sentiment_2.moveToThread(self.thread_3)
            # Step 5: Connect signals and slots
            self.thread_3.started.connect(partial(self.worker_sentiment_2.run, self.webCrawler, self.text , self.since , self.until , self, self.worker_sentiment_2))
            self.worker_sentiment_2.finished.connect(self.thread_3.quit)
            self.worker_sentiment_2.finished.connect(self.worker_sentiment_2.deleteLater)
            self.thread_3.finished.connect(self.thread_3.deleteLater)
            self.thread_3.finished.connect(self.jobDoneThread)
            self.worker_sentiment_2.progress.connect(self.updateProgressBarSentiment)
            self.worker_sentiment_2.returned.connect(self.plotTrend)

            #self.worker.progress.connect(self.reportProgress)
            # Step 6: Start the thread


            self.thread = QThread()
            # Step 3: Create a worker object
            self.worker_trend = Worker_TrendWordWeb()
            # Step 4: Move worker to the thread
            self.worker_trend.moveToThread(self.thread)
            # Step 5: Connect signals and slots
            self.thread.started.connect(partial(self.worker_trend.run, self.webCrawler, self.text , self.since , self.until, self, self.worker_trend))
            self.worker_trend.finished.connect(self.thread.quit)
            self.worker_trend.finished.connect(self.worker_trend.deleteLater)
            self.worker_trend.finished.connect(self.jobDoneThread)
            self.worker_trend.temp.connect(self.updateProgressBar)
            self.worker_trend.returned.connect(self.plotTrendWordWeb)
            self.thread.finished.connect(self.thread.deleteLater)
            #self.worker.progress.connect(self.reportProgress)
            # Step 6: Start the thread

            self.thread_4 = QThread()
            # Step 3: Create a worker object
            self.worker_trend = Worker_TrendWordWeb()
            # Step 4: Move worker to the thread
            self.worker_trend_2.moveToThread(self.thread_4)
            # Step 5: Connect signals and slots
            self.thread_4.started.connect(partial(self.worker_trend_2.run, self.webCrawler, self.text , self.since , self.until, self, self.worker_trend_2))
            self.worker_trend_2.finished.connect(self.thread_4.quit)
            self.worker_trend_2.finished.connect(self.worker_trend_2.deleteLater)
            self.worker_trend_2.finished.connect(self.jobDoneThread)
            self.worker_trend_2.temp.connect(self.updateProgressBar)
            self.worker_trend_2.returned.connect(self.plotTrendWordWeb)
            self.thread_4.finished.connect(self.thread_4.deleteLater)

            self.thread.start()
            self.thread_2.start()
            self.thread_3.start()
            self.thread_4.start()

        else :
            #if only one day can't divide using 1 thread
            print("HDSFSDLKFJDSKLFJDSLKFJDSKLKFj")
            self.waitingThread += 2


            self.thread_2 = QThread()
            self.worker_sentiment = Worker_SentimentWeb()
            # Step 4: Move worker to the thread
            self.worker_sentiment.moveToThread(self.thread_2)
            # Step 5: Connect signals and slots
            self.thread_2.started.connect(partial(self.worker_sentiment.run, self.webCrawler, self.text , self.since , self.until , self, self.worker_sentiment))
            self.worker_sentiment.finished.connect(self.thread_2.quit)
            self.worker_sentiment.finished.connect(self.worker_sentiment.deleteLater)
            self.thread_2.finished.connect(self.thread_2.deleteLater)
            self.thread_2.finished.connect(self.jobDoneThread)
            self.worker_sentiment.progress.connect(self.updateProgressBarSentiment)
            self.worker_sentiment.returned.connect(self.plotTrend)

            #self.worker.progress.connect(self.reportProgress)
            # Step 6: Start the thread


            self.thread = QThread()
            # Step 3: Create a worker object
            self.worker_trend = Worker_TrendWordWeb()
            # Step 4: Move worker to the thread
            self.worker_trend.moveToThread(self.thread)
            # Step 5: Connect signals and slots
            self.thread.started.connect(partial(self.worker_trend.run, self.webCrawler, self.text , self.since , self.until, self, self.worker_trend))
            self.worker_trend.finished.connect(self.thread.quit)
            self.worker_trend.finished.connect(self.worker_trend.deleteLater)
            self.worker_trend.finished.connect(self.jobDoneThread)
            self.worker_trend.temp.connect(self.updateProgressBar)
            self.worker_trend.returned.connect(self.plotTrendWordWeb)
            self.thread.finished.connect(self.thread.deleteLater)
            #self.worker.progress.connect(self.reportProgress)
            # Step 6: Start the thread
            self.thread.start()
            self.thread_2.start()


    def twitThreadDo(self) :

        text = self.lineEdit.text()
        splited_text = text.split(":")
        if len(splited_text) >= 2  :
            self.text = splited_text[0].replace("#","")
            stock_name = splited_text[1]

            self.myThread = QThread()
            self.worker_graphStock = Worker_GraphStock()

            # Step 4: Move worker to the thread
            self.worker_graphStock.moveToThread(self.myThread)
            # Step 5: Connect signals and slots
            self.myThread.started.connect(partial(self.worker_graphStock.run, stock_name , self.since , self.until , self, self.stonk))
            self.worker_graphStock.finished.connect(self.myThread.quit)
            self.worker_graphStock.finished.connect(self.worker_graphStock.deleteLater)
            self.myThread.finished.connect(self.myThread.deleteLater)
            self.worker_graphStock.returned.connect(self.plotStockData)
            #self.worker.progress.connect(self.reportProgress)
            # Step 6: Start the thread
            self.myThread.start()



        else :
            self.text = splited_text[0].replace("#","")
        self.threadTrendWord()
        self.threadSentiment()
        self.threadLocation()



    def updateProgressBar(self, value) :
        #get values to update progress Bar from argument of trendword
        #if over 98 then invisible it
        if value > 98 :
            value = 0
            self.twitterCrawler.progressTrend = 0
            self.progressBar.setVisible(False)
        else :
            self.progressBar.setVisible(True)
        self.progressBar.setValue(value)

    def updateProgressBarSentiment(self, value) :
        #get values to update progress Bar from argument of Sentiment
        #if over 98 then invisible it
        if value > 98 :
            value = 0
            self.twitterCrawler.progressSetiment = 0
            self.progressBarSentiment.setVisible(False)
        else :
            self.progressBarSentiment.setVisible(True)
        self.progressBarSentiment.setValue(value)

    def updateProgressBarHeat(self, value) :
        #get values to update progress Bar from argument of heatmap
        #if over 98 then invisible it
        if value > 98 :
            value = 0
            self.twitterCrawler.progressLocation = 0
            self.progressBarHeat.setVisible(False)
        else :
            self.progressBarHeat.setVisible(True)
        self.progressBarHeat.setValue(value)

    def selectItem(self) :
        ###when secl on list then set to lineEdit
        itms = self.listView.selectedIndexes()
        for it in itms:
            print ('selected item index found at %s with data: %s' % (it.row(), it.data()))
            self.lineEdit.setText(it.data())

    def threadFoliumCommand(self, map) :
        #put html to QWebEngineView
        data = io.BytesIO()
        map.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())
        print("แปะให้แน้ว")


    def threadTrendWord(self) :
        ### threadTrendWord() is method start to seperate date to do thread get trendword of twitter
        #split string from iput
        text = self.lineEdit.text()
        splited_text = text.split(":")
        if len(splited_text) >= 2  :
            self.text = splited_text[0].replace("#","")
            stock_name = splited_text[1]
        else :
            self.text = splited_text[0].replace("#","")

        #date Handler
        self.trendWordList = dict()
        reader = self.twitterCrawler.readingData(since=self.since, until=self.until)
        if (self.since == None and self.until == None  ) :
            print("NOT INSERTED")
            df_analyze = reader[reader.relateHashtag.str.contains(self.text,case=False)]
        elif (self.since != None and self.until != None) :
            print("INSERTED DATE TIME")
            df_analyze = reader[reader.relateHashtag.str.contains(self.text,case=False) &  (reader['date'] > self.since ) & (reader['date'] < self.until )]


        self.twitterCrawler.sizeOfWork = len(df_analyze) #set size of work load

        if (self.since == None and self.until == None ) :
            return 0
        elif (self.since != None and self.until == None ) :
            d1 = datetime.strptime(self.since, "%Y-%m-%d")
        elif (self.since == None and self.until != None ) :
            d2 = datetime.strptime(self.until, "%Y-%m-%d")
        else :
            d1 = datetime.strptime(self.since, "%Y-%m-%d")
            d2 = datetime.strptime(self.until, "%Y-%m-%d")
        dateList = list()
        i = 1
        diff_days = abs((d2 - d1).days)

        #calculate thread count depend on how diff day is
        if (diff_days > 2 ) :
            self.trendThreadSize = 2
        else :
            self.trendThreadSize = 1
        self.waitingThread += self.trendThreadSize

        #calculate date of seperating range
        for k in range(diff_days) :
            d3 = d1+timedelta(days=k)
            if (d3-d1).days > diff_days*i/self.trendThreadSize :
                break

        if self.trendThreadSize == 2 :
            ###start do 2 thread

            self.thread = QThread()
            # Step 3: Create a worker object
            self.worker_trend = Worker_TrendWord()
            # Step 4: Move worker to the thread
            self.worker_trend.moveToThread(self.thread)
            # Step 5: Connect signals and slots
            self.thread.started.connect(partial(self.worker_trend.run, self.twitterCrawler, self.text , self.since , d3.strftime("%Y-%m-%d") , self, self.worker_trend))
            self.worker_trend.finished.connect(self.thread.quit)
            #self.worker_trend.finished.connect(self.worker_trend.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(self.jobDoneThread) #collecting data after thread
            #self.worker.progress.connect(self.reportProgress)
            self.worker_trend.returned.connect(self.collecting) #collecting result data
            self.worker_trend.temp.connect(self.updateProgressBar) #input pyqtsignal to update progressbar

            self.thread2 = QThread()
            # Step 3: Create a worker object
            self.worker_trend2 = Worker_TrendWord()
            # Step 4: Move worker to the thread
            self.worker_trend2.moveToThread(self.thread2)
            # Step 5: Connect signals and slots
            self.thread2.started.connect(partial(self.worker_trend2.run, self.twitterCrawler, self.text , d3.strftime("%Y-%m-%d") , self.until , self, self.worker_trend2))
            self.worker_trend2.finished.connect(self.thread2.quit)
            #self.worker_trend2.finished.connect(self.worker_trend2.deleteLater)
            self.thread2.finished.connect(self.thread2.deleteLater)
            self.thread2.finished.connect(self.jobDoneThread)
            #self.worker.progress.connect(self.reportProgress)
            self.worker_trend2.returned.connect(self.collecting) #collecting result, return data
            self.worker_trend2.temp.connect(self.updateProgressBar) #update progress bar after temp is emiting singal

            # Step 6: Start the thread
            self.thread2.start()
            self.thread.start()

        else :
            self.thread = QThread()
            # Step 3: Create a worker object
            self.worker_trend = Worker_TrendWord()
            # Step 4: Move worker to the thread
            self.worker_trend.moveToThread(self.thread)
            # Step 5: Connect signals and slots
            self.thread.started.connect(partial(self.worker_trend.run, self.twitterCrawler, self.text , self.since , self.until , self, self.worker_trend))
            self.worker_trend.finished.connect(self.thread.quit)
            #self.worker_trend.finished.connect(self.worker_trend.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(self.jobDoneThread)
            #self.worker.progress.connect(self.reportProgress)
            self.worker_trend.returned.connect(self.collecting)
            self.worker_trend.temp.connect(self.updateProgressBar)
            self.thread.start()



    def collecting(self, object) :
        for k in object :
            print(k)
            if k[0] in self.trendWordList.keys() :
                self.trendWordList[k[0]] += k[1]
            else :
                self.trendWordList[k[0]] = k[1]

    def threadSentiment(self) :
        self.jobDoneSentiment = 0
        text = self.lineEdit.text()
        splited_text = text.split(":")
        if len(splited_text) >= 2  :
            self.text = splited_text[0].replace("#","")
            stock_name = splited_text[1]
        else :
            self.text = splited_text[0].replace("#","")

        self.sentimentList = dict()
        reader = self.twitterCrawler.readingData(since=self.since, until=self.until)
        if (self.since == None and self.until == None  ) :
            print("NOT INSERTED")
            df_analyze = reader[reader.relateHashtag.str.contains(self.text,case=False)]
        elif (self.since != None and self.until != None) :
            print("INSERTED DATE TIME")
            df_analyze = reader[reader.relateHashtag.str.contains(self.text,case=False) &  (reader['date'] > self.since ) & (reader['date'] < self.until )]



        self.twitterCrawler.sizeOfWorkSentiment = len(df_analyze)

        if (self.since == None and self.until == None ) :
            return 0
        elif (self.since != None and self.until == None ) :
            d1 = datetime.strptime(self.since, "%Y-%m-%d")
        elif (self.since == None and self.until != None ) :
            d2 = datetime.strptime(self.until, "%Y-%m-%d")
        else :
            d1 = datetime.strptime(self.since, "%Y-%m-%d")
            d2 = datetime.strptime(self.until, "%Y-%m-%d")
        dateList = list()
        i = 1
        diff_days = abs((d2 - d1).days)


        if (diff_days > 8) :
            self.sentimentThreadSize=4
        elif (diff_days > 2 ) :
            self.sentimentThreadSize=2
        else :
            self.sentimentThreadSize=1

        self.waitingThread += self.sentimentThreadSize

        for j in range(diff_days) :
            d3 = d1+timedelta(days=j)
            if (d3-d1).days > diff_days*i/self.sentimentThreadSize :
                day_gap = (d3-d1).days
                d4 = d3+timedelta(days=day_gap)
                d5 = d4+timedelta(days=day_gap)
                break

        if (self.sentimentThreadSize==4) :

            self.thread_3 = QThread()
            self.worker_sentiment = Worker_Sentiment()
            # Step 4: Move worker to the thread
            self.worker_sentiment.moveToThread(self.thread_3)
            # Step 5: Connect signals and slots
            self.thread_3.started.connect(partial(self.worker_sentiment.run, self.twitterCrawler, self.text , self.since , d3.strftime("%Y-%m-%d") , self,self.worker_sentiment))
            self.worker_sentiment.finished.connect(self.thread_3.quit)
            #self.worker_sentiment.finished.connect(self.worker_sentiment.deleteLater)
            self.thread_3.finished.connect(self.thread_3.deleteLater)
            self.thread_3.finished.connect(self.jobDoneThread)
            self.worker_sentiment.returned.connect(self.collectingSentimentAfterThread)
            self.worker_sentiment.progress.connect(self.updateProgressBarSentiment)
            #self.worker.progress.connect(self.reportProgress)
            # Step 6: Start the thread


            self.thread_4 = QThread()
            self.worker_sentiment2 = Worker_Sentiment()
            # Step 4: Move worker to the thread
            self.worker_sentiment2.moveToThread(self.thread_4)
            # Step 5: Connect signals and slots
            self.thread_4.started.connect(partial(self.worker_sentiment2.run, self.twitterCrawler, self.text , d3.strftime("%Y-%m-%d") , d4.strftime("%Y-%m-%d") , self,self.worker_sentiment2))
            self.worker_sentiment2.finished.connect(self.thread_4.quit)
            #self.worker_sentiment2.finished.connect(self.worker_sentiment2.deleteLater)
            self.thread_4.finished.connect(self.thread_4.deleteLater)
            self.thread_4.finished.connect(self.jobDoneThread)
            self.worker_sentiment2.returned.connect(self.collectingSentimentAfterThread)
            self.worker_sentiment2.progress.connect(self.updateProgressBarSentiment)

            self.thread_7 = QThread()
            self.worker_sentiment3 = Worker_Sentiment()
            # Step 4: Move worker to the thread
            self.worker_sentiment3.moveToThread(self.thread_7)
            # Step 5: Connect signals and slots
            self.thread_7.started.connect(partial(self.worker_sentiment3.run, self.twitterCrawler, self.text , d4.strftime("%Y-%m-%d") , d5.strftime("%Y-%m-%d") , self,self.worker_sentiment3))
            self.worker_sentiment3.finished.connect(self.thread_7.quit)
            #self.worker_sentiment2.finished.connect(self.worker_sentiment2.deleteLater)
            self.thread_7.finished.connect(self.thread_7.deleteLater)
            self.thread_7.finished.connect(self.jobDoneThread)
            self.worker_sentiment3.returned.connect(self.collectingSentimentAfterThread)
            self.worker_sentiment3.progress.connect(self.updateProgressBarSentiment)


            self.thread_8 = QThread()
            self.worker_sentiment4 = Worker_Sentiment()
            # Step 4: Move worker to the thread
            self.worker_sentiment4.moveToThread(self.thread_8)
            # Step 5: Connect signals and slots
            self.thread_8.started.connect(partial(self.worker_sentiment4.run, self.twitterCrawler, self.text , d5.strftime("%Y-%m-%d") , self.until , self,self.worker_sentiment4))
            self.worker_sentiment4.finished.connect(self.thread_8.quit)
            #self.worker_sentiment2.finished.connect(self.worker_sentiment2.deleteLater)
            self.thread_8.finished.connect(self.thread_8.deleteLater)
            self.thread_8.finished.connect(self.jobDoneThread)
            self.worker_sentiment4.returned.connect(self.collectingSentimentAfterThread)
            self.worker_sentiment4.progress.connect(self.updateProgressBarSentiment)
            #self.worker.progress.connect(self.reportProgress)
            # Step 6: Start the thread
            self.thread_4.start()
            self.thread_3.start()
            self.thread_7.start()
            self.thread_8.start()

        elif (self.sentimentThreadSize==2):

            self.thread_3 = QThread()
            self.worker_sentiment = Worker_Sentiment()
            # Step 4: Move worker to the thread
            self.worker_sentiment.moveToThread(self.thread_3)
            # Step 5: Connect signals and slots
            self.thread_3.started.connect(partial(self.worker_sentiment.run, self.twitterCrawler, self.text , self.since , d3.strftime("%Y-%m-%d") , self,self.worker_sentiment))
            self.worker_sentiment.finished.connect(self.thread_3.quit)
            #self.worker_sentiment.finished.connect(self.worker_sentiment.deleteLater)
            self.thread_3.finished.connect(self.thread_3.deleteLater)
            self.thread_3.finished.connect(self.jobDoneThread)
            self.worker_sentiment.returned.connect(self.collectingSentimentAfterThread)
            self.worker_sentiment.progress.connect(self.updateProgressBarSentiment)
            #self.worker.progress.connect(self.reportProgress)
            # Step 6: Start the thread


            self.thread_4 = QThread()
            self.worker_sentiment2 = Worker_Sentiment()
            # Step 4: Move worker to the thread
            self.worker_sentiment2.moveToThread(self.thread_4)
            # Step 5: Connect signals and slots
            self.thread_4.started.connect(partial(self.worker_sentiment2.run, self.twitterCrawler, self.text , d3.strftime("%Y-%m-%d") , self.until , self,self.worker_sentiment2))
            self.worker_sentiment2.finished.connect(self.thread_4.quit)
            #self.worker_sentiment2.finished.connect(self.worker_sentiment2.deleteLater)
            self.thread_4.finished.connect(self.thread_4.deleteLater)
            self.thread_4.finished.connect(self.jobDoneThread)
            self.worker_sentiment2.returned.connect(self.collectingSentimentAfterThread)
            self.worker_sentiment2.progress.connect(self.updateProgressBarSentiment)

            self.thread_4.start()
            self.thread_3.start()

        else :

            self.thread_3 = QThread()
            self.worker_sentiment = Worker_Sentiment()
            # Step 4: Move worker to the thread
            self.worker_sentiment.moveToThread(self.thread_3)
            # Step 5: Connect signals and slots
            self.thread_3.started.connect(partial(self.worker_sentiment.run, self.twitterCrawler, self.text , self.since , self.until , self,self.worker_sentiment))
            self.worker_sentiment.finished.connect(self.thread_3.quit)
            #self.worker_sentiment.finished.connect(self.worker_sentiment.deleteLater)
            self.thread_3.finished.connect(self.thread_3.deleteLater)
            self.thread_3.finished.connect(self.jobDoneThread)
            self.worker_sentiment.returned.connect(self.collectingSentimentAfterThread)
            self.worker_sentiment.progress.connect(self.updateProgressBarSentiment)

            self.thread_3.start()
            #self.worker.progress.connect(self.reportProgress)


    def collectingSentimentAfterThread(self, data) :
        ###collecting result after each thread done

        #update frequency of sentiment
        for k in data :
            print(k)
            if k in self.sentimentList.keys() :
                self.sentimentList[k] += data[k]
            else :
                self.sentimentList[k] = data[k]
        self.jobDoneSentiment += 1
        if (self.jobDoneSentiment == self.sentimentThreadSize ) :
            #if collect all update sentiment
            self.updateProgressBarSentiment(100)
            self.plotTrend(self.sentimentList)


    def threadLocation(self) :
        ##calling thread find heatmap to do with divide pool thread to do
        self.df = pd.DataFrame(columns= ["location","latitude","longitude","count"] )
        text = self.lineEdit.text()
        splited_text = text.split(":")
        if len(splited_text) >= 2  :
            self.text = splited_text[0].replace("#","")
            stock_name = splited_text[1]
        else :
            self.text = splited_text[0].replace("#","")

        self.sentimentList = dict()
        reader = self.twitterCrawler.readingData(since=self.since, until=self.until)
        count = 0

        for tweet in reader["place"] : #in dataframe col "place"

            if not pd.isna(tweet) :  #is not empty or NaN
                tweet = tweet.lower()
                boolValues = False
                for badChar in self.badLocation :
                    if tweet.find(badChar) != -1 :
                        print(tweet, badChar ,"text found")
                        boolValues = True
                        break
                if  (re.search(self.emoji_pattern, tweet) != None) or boolValues   :
                    print("Found Emoji and bad char", tweet, (re.search(self.emoji_pattern, tweet) != None),boolValues)
                    pass
                else :
                    count += 1

        self.twitterCrawler.sizeOfWorkLocation = count



        if (self.since == None and self.until == None ) :
            return 0
        elif (self.since != None and self.until == None ) :
            d1 = datetime.strptime(self.since, "%Y-%m-%d")
        elif (self.since == None and self.until != None ) :
            d2 = datetime.strptime(self.until, "%Y-%m-%d")
        else :
            d1 = datetime.strptime(self.since, "%Y-%m-%d")
            d2 = datetime.strptime(self.until, "%Y-%m-%d")
        dateList = list()
        i = 1
        diff_days = abs((d2 - d1).days)


        if (diff_days > 2 ) :
            self.locationThreadSize=2
        else :
            self.locationThreadSize=1

        self.waitingThread += self.locationThreadSize

        for k in range(diff_days) :
            d3 = d1+timedelta(days=k)
            if (d3-d1).days > diff_days*i/self.locationThreadSize :
                break
        if (self.locationThreadSize == 2 ) :
            self.thread_5 = QThread()
            self.worker_heatmap = Worker_heatmap()
            # Step 4: Move worker to the thread
            self.worker_heatmap.moveToThread(self.thread_5)
            # Step 5: Connect signals and slots
            self.thread_5.started.connect(partial(self.worker_heatmap.run, self.twitterCrawler, self.text , self.since , d3.strftime("%Y-%m-%d") , self, self.worker_heatmap))
            self.worker_heatmap.finished.connect(self.thread_5.quit)
            #self.worker_sentiment.finished.connect(self.worker_sentiment.deleteLater)
            self.thread_5.finished.connect(self.thread_5.deleteLater)
            self.thread_5.finished.connect(self.jobDoneThread)
            self.worker_heatmap.returned.connect(self.collectingLocationAfterThread)
            self.worker_heatmap.progress.connect(self.updateProgressBarHeat)
            #self.worker.progress.connect(self.reportProgress)
            # Step 6: Start the thread


            self.thread_6 = QThread()
            self.worker_heatmap2 = Worker_heatmap()
            # Step 4: Move worker to the thread
            self.worker_heatmap2.moveToThread(self.thread_6)
            # Step 5: Connect signals and slots
            self.thread_6.started.connect(partial(self.worker_heatmap2.run, self.twitterCrawler, self.text ,  d3.strftime("%Y-%m-%d") , self.until  , self, self.worker_heatmap2))
            self.worker_heatmap2.finished.connect(self.thread_6.quit)
            #self.worker_sentiment.finished.connect(self.worker_sentiment.deleteLater)
            self.thread_6.finished.connect(self.thread_6.deleteLater)
            self.thread_6.finished.connect(self.jobDoneThread)
            self.worker_heatmap2.returned.connect(self.collectingLocationAfterThread)
            self.worker_heatmap2.progress.connect(self.updateProgressBarHeat)
            #self.worker.progress.connect(self.reportProgress)
            # Step 6: Start the thread
            #self.worker.progress.connect(self.reportProgress)
            # Step 6: Start the thread

            self.thread_5.start()
            self.thread_6.start()

        else :

            self.thread_5 = QThread()
            self.worker_heatmap = Worker_heatmap()
            # Step 4: Move worker to the thread
            self.worker_heatmap.moveToThread(self.thread_5)
            # Step 5: Connect signals and slots
            self.thread_5.started.connect(partial(self.worker_heatmap.run, self.twitterCrawler, self.text , self.since , self.until , self, self.worker_heatmap))
            self.worker_heatmap.finished.connect(self.thread_5.quit)
            #self.worker_sentiment.finished.connect(self.worker_sentiment.deleteLater)
            self.thread_5.finished.connect(self.thread_5.deleteLater)
            self.thread_5.finished.connect(self.jobDoneThread)
            self.worker_heatmap.returned.connect(self.collectingLocationAfterThread)
            self.worker_heatmap.progress.connect(self.updateProgressBarHeat)
            self.thread_5.start()

    def collectingLocationAfterThread(self, data) :
        ##collecting data after thread work
        frame = [self.df, data]
        self.df = pd.concat(frame)
        map = self.twitterCrawler.foliumPlotMarker(self.df)
        map.save("shh.html")
        self.threadFoliumCommand(map)

    def jobDoneThread(self) :
        ### thread counting
        self.doneThread += 1
        if self.doneThread == self.waitingThread :
            self.doneThread = 0
            self.waitingThread = 0
            self.pushButton.setEnabled(True) #enable button
            self.pushButton_2.setEnabled(True)














if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
