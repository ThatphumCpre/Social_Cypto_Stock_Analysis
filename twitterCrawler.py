import time
start = time.time()
import tweepy
import pandas as pd
import pythainlp.util
import spacy
import matplotlib.pyplot as plt
import emoji
import re
from pythainlp.corpus.common import thai_words
from pythainlp import Tokenizer
from pythainlp.corpus import thai_stopwords
from nltk.corpus import stopwords
import numpy as np
import os
from datetime import datetime
from datetime import timedelta
import folium
from geopy.geocoders import Nominatim
from pythainlp.util import dict_trie
import deepcut
from sentiment import Sentiment
import pickle
import io
from threading import Thread
from operator import itemgetter
print(time.time()-start)

#from PyQt5 import QtCore, QtGui, QtWidgets,QtWebEngineWidgets

class Trendy :


    def __init__(self, pBar=None) :

        self.count = 0
        self.progressTrend = 0
        self.tester = None
        self.sizeOfWork = 0 #size of workload that need to analyze  trend words

        self.progressSetiment = 0 #progress bar percent of sentiment
        self.sizeOfWorkSentiment = 0 #size of workload that need to analyze of geopy
        self.worker_sentiment = None #variable that collect qthread worker  of sentiment

        self.worker_Location = None  #variable that collect qthread worker  of geopy
        self.sizeOfWorkLocation = 0  #size of workload that need to analyze of geopy
        self.progressLocation = 0 #progress bar percent of geopy

        self.fileNameTwitter = "twitterCrawler" #name of twitter data file
        self.stop_words = set(stopwords.words("english")) #create set of english stop words
        self.specialChar = [" ",":","/","#","@",'.', ",","?", '\n', '&', ';', "…", "^", "https", "the"] #special Char list for cleans
        self.badLocation = [":","/","#","@","?",'&', ';', "…", "^","♡","♪","･","!","♥"] #badCharacter that we didn't want in context
        self.extThaiword = ["นะคะ","นะครับ","ค่ะ","คะ","ครับ","ครับผม","กก","งง","หรือว่า","เหรอ","หรอ","ล่ะ"] #extend word for thai stop word
        self.thai_stopwords = set(thai_stopwords()) #create set of thai stop words
        self.thai_stopwords = self.thai_stopwords.union(set(self.extThaiword)) #union set of stopwords and extend Stopword
        self.emoji_pattern = re.compile("["
                                    u"\U0001F600-\U0001F64F"  # emoticons
                                    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                    u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                    "]+", flags=re.UNICODE)
        self.badPos = ["AUX","ADP","SCONJ", "DET","PART","CCONJ","NUM","PROPN"] #pos of english that we din't want
        ### twitter key
        self.consumer_key = "__twitter_key"
        self.consumer_secret = "__twitter_key"
        self.access_token = "__twitter_key"
        self.access_token_secret = "__twitter_key"

        ####instance authentickey
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(auth)

        try :
            self.df = pd.read_csv("{}.csv".format(self.fileNameTwitter))
            print("find")
        except :
            self.df = pd.DataFrame(columns= ["tweet","user","relateHashtag","date","place"] )

    def findAndCombineLocation(self, keyword, since=None, until=None, worker=None) :
        self.isValidSinceUntil(since, until)
        if worker != None :
            #if have argument qthread for progress bar
            self.worker_Location = worker  #set qthread worker as attribute

        try :
            reader = pd.read_csv("{}/temp/{}_{}_{}_map.csv".format(os.getcwd(), keyword.replace("#", ""),since, until))
            #load excactly date
            return reader #return result

        except FileNotFoundError :
            data = dict()
            if (since != None and until != None ) :
                since_obj = datetime.strptime(since, "%Y-%m-%d")
                until_obj = datetime.strptime(until, "%Y-%m-%d")
            elif (since != None and until == None ) :
                since_obj = datetime.strptime(since, "%Y-%m-%d")
            elif (since == None and until != None ) :
                until_obj = datetime.strptime(until, "%Y-%m-%d")
            else :
                print("No Date")


            cacheList = os.listdir("{}/temp".format(os.getcwd())) #list of cache file (saved result )
            selectedName = ""  #variable for collect selected Name
            selectedSince = "" #variable for collect selected Since
            selectedUntil = "" #variable for collect seleected Until
            selectedDiffSince = 0 #variable for collect different since
            selectedDiffUntil = 0 #vairable for collect differnt until
            maxDiff = float('-inf') #most less values
            for fileName in cacheList :
                tempFileName = fileName.split("_") #split name {keyword}_{since}_{until}_map.csv
                if ( len(tempFileName) == 4 and tempFileName[1] != "web" )  :
                    if(tempFileName[0] == keyword) :
                        temp = tempFileName[3].split(".") #split map.csv to type
                        type = temp[1] #collecting type
                        print("::::::::::", tempFileName[1],tempFileName,"DSDDSADASD")
                        since_tartget = datetime.strptime(tempFileName[1], "%Y-%m-%d") #convert since to datetime object
                        until_tartget = datetime.strptime(tempFileName[2], "%Y-%m-%d") #convert until to datetime object
                        diff_since = ((since_tartget - since_obj).days) #calculate different of since
                        diff_until = ((until_obj - until_tartget).days) #calculate different of until
                        sumDiff = diff_since + diff_until #sumation diff
                        print(type, diff_since, diff_until, fileName)
                        if (type == "csv" and sumDiff > maxDiff and diff_since >= 0 and diff_until >= 0) :
                            #find most relative since and date   and save selected file
                            selectedName = fileName
                            selectedSince = since_tartget
                            selectedUntil = until_tartget
            print("selected file name is : ", selectedName)
            if selectedName != "" :
                #recursion case
                df_temp= pd.read_csv("{}/temp/{}".format(os.getcwd(),selectedName)) #find selected file

                leftSidePandas= self.findAndCombineLocation(keyword,since=since,until=selectedSince.strftime("%Y-%m-%d")) #file other left side date
                rightSidePandas = self.findAndCombineLocation(keyword,since=selectedUntil.strftime("%Y-%m-%d"),until=until) #find other right side date
                self.sizeOfWorkLocation -= len(leftSidePandas) + len(rightSidePandas) #decrease workload after
                frame = [leftSidePandas, rightSidePandas] #concat dataframe
                self.df = pd.concat(frame)
                return self.df #return result
            else :
                #base case
                return self.geopyToPandas(keyword, since ,until) #if not found file the return renew process

    def findAndCombineSentiment(self, keyword, since=None, until=None, worker=None) :
        ### findAndCombineTrend() get argumment keyword to sentiment analyze in database to return in dict of sentiment result {pos, neg, neu}
        ### if have cache file (saved result) then use it and find excludeed file that need to processed
        self.isValidSinceUntil(since, until) #validation of since and until
        if worker != None :
            #if have argument of qthread
            self.worker_sentiment = worker #set  as attribute to update progressbar
        try :
            ### base case
            with open('{}/temp/{}_{}_{}.pkl'.format(os.getcwd(),keyword,since,until), 'rb') as handle:
            #if find excactly date file
                result = pickle.load(handle)  #loadind pickled file
            return result  #return

        except FileNotFoundError :

            #date exception
            if (since == None and until == None ) :
                return self.getTrendWordData(keyword)
            elif (since != None and until == None ) :
                since_obj = datetime.strptime(since, "%Y-%m-%d")
            elif (since == None and until != None ) :
                until_obj = datetime.strptime(until, "%Y-%m-%d")
            else :
                since_obj = datetime.strptime(since, "%Y-%m-%d")
                until_obj = datetime.strptime(until, "%Y-%m-%d")


            cacheList = os.listdir("{}/temp".format(os.getcwd())) #listed of cache file
            selectedName = "" #vairable selected file name
            selectedSince = "" #variable selected file since
            selectedUntil = "" #variable selected file until
            selectedDiffSince = 0 #different of since
            selectedDiffUntil = 0 #different of until
            maxDiff = float('-inf') #most less values
            for fileName in cacheList :
                tempFileName = fileName.split("_") #split file name {keyword}_{since}_{until}.pkl
                if ( len(tempFileName) == 3 )  :
                    if(tempFileName[0] == keyword) :
                        temp = tempFileName[2].split(".") #split until from type {until}.pkl
                        tempFileName[2] = temp[0] #until
                        type = temp[1]  #save type to variable
                        since_tartget = datetime.strptime(tempFileName[1], "%Y-%m-%d") #convert sting date since to datetime
                        until_tartget = datetime.strptime(tempFileName[2], "%Y-%m-%d") #convert sting date until to datetime
                        diff_since = ((since_tartget - since_obj).days) #calculate different of since
                        diff_until = ((until_obj - until_tartget).days) #calculate different of until
                        sumDiff = diff_since + diff_until #sumation of diff
                        print(type, diff_since, diff_until, fileName)
                        if (type == "pkl" and sumDiff > maxDiff and diff_since >= 0 and diff_until >= 0) :
                            #saving most relate cache file
                            selectedName = fileName
                            selectedSince = since_tartget
                            selectedUntil = until_tartget

            print("selected file name is : ", selectedName)
            if selectedName != "" :
                #recursive case
                with open('{}/temp/{}'.format(os.getcwd(),selectedName), 'rb') as handle:
                #if find sentiment.pkl
                    result = pickle.load(handle) #open selected most relate file

                leftSideSentiment = self.sentimenTweet(keyword,since=since,until=selectedSince.strftime("%Y-%m-%d")) #find most relative at left side
                rightSideSentiment = self.sentimenTweet(keyword,since=selectedUntil.strftime("%Y-%m-%d"),until=until) #find most relative at right size
                self.sizeOfWorkSentiment -= len(leftSideSentiment) + len(rightSideSentiment) #decreaseing workload

                #update  result from left side rightside
                for k in leftSideSentiment  :
                    result[k] += leftSideSentiment[k]
                for k in rightSideSentiment  :
                    result[k] += rightSideSentiment[k]

                return result #return data
            else :
                ###base case
                return self.sentimenTweet(keyword, since=since, until=until) #not found relate file

    def findAndCombineTrend(self, keyword, since=None, until=None, test=None) :
        ### findAndCombineTrend() concat and combine result cache that processed then analyze trendword exclude date
        ### return result in list of tulle with pair of (word, count)
        self.isValidSinceUntil(since, until) #validation since and until

        if test != None :
            #if input qthread to emit progress bar
            self.tester = test #set passing object of qthread to attribute
        try :
            ### base case

            reader = pd.read_csv("{}/temp/{}_{}_{}.csv".format(os.getcwd(), keyword.replace("#", ""),since, until))
            #try to read excactly date of cache saved result file
            data = list()

            for index, col in reader.iterrows() :
                data.append((col["word"],col["count"]))
                #append to list with pair of (word, count )
            return data #return result

        except FileNotFoundError :

            print("hi",since, until)
            if (since == None and until == None ) :
                return self.getTrendWordData(keyword)
            elif (since != None and until == None ) :
                since_obj = datetime.strptime(since, "%Y-%m-%d")
            elif (since == None and until != None ) :
                until_obj = datetime.strptime(until, "%Y-%m-%d")
            else :
                since_obj = datetime.strptime(since, "%Y-%m-%d")
                until_obj = datetime.strptime(until, "%Y-%m-%d")


            cacheList = os.listdir("{}/temp".format(os.getcwd())) #getcwd from cache list (saved result )
            selectedName = "" #vairable for collect name selected file
            selectedSince = "" #variable for collect since selected file
            selectedUntil = "" #variable for collect Until selected file
            selectedDiffSince = 0 #different of since
            selectedDiffUntil = 0 #different of until
            maxDiff = float('-inf') #lowest values
            for fileName in cacheList :
                tempFileName = fileName.split("_") #split name of cache file {keyword}_{since}_{until}.csv
                if ( len(tempFileName) == 3 )  :
                    if(tempFileName[0] == keyword) : #correspond to argument keyword
                        temp = tempFileName[2].split(".")  #split type of file (.csv)
                        tempFileName[2] = temp[0]   #temp collect until
                        type = temp[1] #type file
                        since_tartget = datetime.strptime(tempFileName[1], "%Y-%m-%d") #convert to datetime object since
                        until_tartget = datetime.strptime(tempFileName[2], "%Y-%m-%d") #convert to datetime object until
                        diff_since = ((since_tartget - since_obj).days) #finderent of since
                        diff_until = ((until_obj - until_tartget).days) #find different of until
                        sumDiff = diff_since + diff_until #sumation of different
                        print(type, diff_since, diff_until, fileName)
                        if (type == "csv" and sumDiff > maxDiff and diff_since >= 0 and diff_until >= 0) :
                            #if most relate date then collect file name
                            selectedName = fileName
                            selectedSince = since_tartget
                            selectedUntil = until_tartget

            print("selected file name is : ", selectedName)

            if selectedName != "" :
                #recursion case
                reader = pd.read_csv("{}/temp/{}".format(os.getcwd(),selectedName)) #reading selected file
                data = dict()
                for index, col in reader.iterrows() :
                    #add to data
                    data[col['word']] = col['count']

                print("hii",since,selectedSince.strftime("%Y-%m-%d"))
                leftSide = self.findAndCombineTrend(keyword,since=since,until=selectedSince.strftime("%Y-%m-%d")) #recursion to file more left
                rightSide = self.findAndCombineTrend(keyword,since=selectedUntil.strftime("%Y-%m-%d"),until=until) #recursion to find more right
                self.sizeOfWork -= len(leftSide) + len(rightSide) #update workload

                for k in leftSide :
                    #concat file select to data
                    if k[0] in data.keys() :
                        data[k[0]] +=  k[1]
                    else :
                        data[k[0]] = k[1]

                for k in rightSide :
                    #concat file select rightside to data
                    if k[0] in data.keys() :
                        data[k[0]] +=  k[1]
                    else :
                        data[k[0]] = k[1]

                tm = datetime.now()
                tm_rounded = pd.Series(tm).dt.round('1min')
                time = tm_rounded.at[0]

                items = list(data.items()) #sortting items
                items.sort(key=itemgetter(1), reverse=True)


                tempDF = pd.DataFrame(columns= ["word","count","date","range"] ) #

                for k in range(len(items)) :
                    new_column = pd.Series([items[k][0], items[k][1], time,  "{},{}".format(since,until) ], index=tempDF.columns)
                    tempDF = tempDF.append(new_column,ignore_index=True)
                keyword.replace("#","")
                tempDF.to_csv("{}/temp/{}_{}_{}.csv".format(os.getcwd(), keyword,since,until), index=False, mode="w") #save temp

                return items

            else :
                #base case not fond file correspodn try to analyze from database
                print("NoT FOUN CO FILE ", keyword, since, since)
                return self.getTrendWordData(keyword, since=since, until=until)

    def viewTrends(self, woeid = 23424960 , rank=10) :
        #view trends now from woeid
        trends = self.api.trends_place(id = woeid)
        trendItems = list()
        n = 0
        for value in trends: #access data
            for trend in value["trends"]:  #access dict key
                #print(trend["name"],trend["tweet_volume"])
                if (trend["name"].find("#") != -1 ) :
                    #append each hashtag to list
                    trendItems.append(trend["name"].lower())
                    n += 1
                if (n > rank) :
                    break
        return trendItems #return list of hashtag collected

    def sentimenTweet(self, keyword, since=None, until=None) :
        ### sentimentTweet() get argumment keyword to sentiment analyze in database to return in dict of sentiment result {pos, neg, neu}
        self.isValidSinceUntil(since, until) #validation of since and until
        try :
            with open('{}/temp/{}_{}_{}.pkl'.format(os.getcwd(),keyword,since,until), 'rb') as handle:
            #if find sentiment.pkl
                result = pickle.load(handle)  #loading temp file
        except :
            #if not found cache file
            sentiment = Sentiment() #instance sentiment analysis tools
            reader = self.readingData(since=since, until=until) #reading database included day to pandas dataframe
            if (since == None and until == None  ) :
                df_sentiment = reader[reader['relateHashtag'].str.contains(keyword,case=False)]
            elif (since != None and until == None) :
                df_sentiment = reader[reader['date'].str.contains(since,case=False) & reader['relateHashtag'].str.contains(keyword,case=False) ]
            elif (since != None and until != None) :
                print(   (reader['date'] <= until ))
                df_sentiment = reader[ (reader['date'] >= since ) & (reader['date'] <= until ) & (reader['relateHashtag'].str.contains(keyword,case=False) )]
            if (len(df_sentiment) == 0 ) :
                print("Didn't Found Keyword in data")

            pos, neg, neu = 0, 0, 0 #counting variable
            c=0
            for k in df_sentiment['tweet'] :
                #in range of tweet
                print(c)
                c += 1
                result = sentiment.sentiment(k) #sentiment analysis
                print(result)
                #frequency count of neg pos neu result after analyze
                if result == "neg" :
                    neg += 1
                elif result == "pos" :
                    pos += 1
                else :
                    neu += 1

                if self.worker_sentiment != None :
                    #if have qthread
                    self.progressSetiment += (1/self.sizeOfWorkSentiment)*100 #calculate updation of progress
                    self.worker_sentiment.progress.emit(self.progressSetiment) #emit pyqtSignal to update progressbar from now progress

            print(pos, neu, neg)
            result = {"Positive":pos, "Neutral":neu, "Negative":neg}
            print("saved",'{}/temp/{}_{}_{}.pkl'.format(os.getcwd(), keyword,since,until))
            with open('{}/temp/{}_{}_{}.pkl'.format(os.getcwd(), keyword,since,until), 'wb') as handle:
                #pikled result
                    pickle.dump(result, handle)
        return result #return result

    def getTrendWordData(self, keyword, since=None, until=None) :
        ### getTrendData is analyze trend word of twitter handle exception and cache load
        ### get argument keyword to get trend word keyword hashtag with tuple of (word,count)
        self.isValidSinceUntil(since, until) #check valid of since and until

        try :
            temp = keyword #collect keyword to temp
            reader = pd.read_csv("{}/temp/{}_{}_{}.csv".format(os.getcwd(),temp.replace("#", ""),since, until)) #try to load cache file
            data = list() #temp list to return and collecting pair of count and word
            readingSince, readingUntil = reader["range"][1].split(",") #read since and until

            if  (readingSince == since and readingUntil == until) or (readingSince == None and readingUntil  == None ) :
                for index, col in reader.iterrows() :
                    data.append((col["word"],col["count"])) #appends pair of word, count in temp file
                return data #return result data
            else :
                return self.analyze(keyword, since=since, until=until, plot=False) #get new data that not analyze

        except :
            #file not found
            if not "temp" in os.listdir() : #if not have temp folder to collect cache
                os.mkdir("temp")
            try :
                return self.analyze(keyword, since=since, until=until, plot=False) #analyzing new data
            except :
                return self.analyze(keyword, since=since, until=until, lang="en",plot=False)

    def analyze(self, keyword, since=None, until=None, lang="th", plot=False) :
        ### analyze() is method that have parameter keyword to analyze frequency of each word and return in list of tuple (word, count )

        self.isValidSinceUntil(since, until) #checking is since and until is valid
        keyword = keyword.replace("#","") #remove '#' in keyword
        self.sp = spacy.load("en_core_web_sm") #loading spacy (word tokenizer of english lang)
        keyword = keyword.lower() #convert keyword to lower
        data = dict() #dictionary that counting pair of (word, count)
        words = set(thai_words())           #create set of nlp data
        words.add(keyword)     #add keyword to data set
        trie = dict_trie(dict_source=words)
        #custom_tokenizer_deepcut = Tokenizer(trie, engine="deepcut") #create new tokenize from custom dataset
        custom_tokenizer_newmm = Tokenizer(trie) #create new tokenize from custom dataset


        reader = self.readingData(since=since, until=until) #reading reader pandas dataframe from database
        if (since == None and until == None  ) :
            df_analyze = reader[reader.relateHashtag.str.contains(keyword,case=False)]
        elif (since != None and until != None) :
            df_analyze = reader[reader.relateHashtag.str.contains(keyword,case=False) &  (reader['date'] > since ) & (reader['date'] < until )]

        if (len(df_analyze) < 50  ) :
            print("Didn't Found Keyword in data")
            self.df_analyze = self.readingData(since=since, until=until)
            #self.collectData(keyword ,quantity=50, lastDateTime=since, mode="w" , until=until, lang=lang)
            df_analyze = reader[reader.relateHashtag.str.contains(keyword,case=False) &  (reader['date'] >= since ) & (reader['date'] <= until )]


        for tweet in df_analyze["tweet"] :

            if  (self.tester != None ) :
                #if contains qthread object
                self.progressTrend += (1/self.sizeOfWork)*100
                self.tester.temp.emit(int(self.progressTrend)) #emit pyqtSignal to update  progressbar

            m = re.search("[ก-๛]", tweet) #using re to find thai char in tweet
            if ( m != None ) :
                #if found thai char
                each_thaiword = custom_tokenizer_newmm.word_tokenize(tweet) #tokenized from custom tokenizer that include keyword
                #each_thaiword = pythainlp.tokenize.word_tokenize(word.text, engine='newmm')
                for thaiword in each_thaiword :
                    for badChar in self.specialChar :
                        if (thaiword.find(badChar) != -1
                                             or thaiword in self.thai_stopwords
                                             or len(thaiword) < 3
                                             or self.isRepeatChar(thaiword)
                                             or thaiword.find(keyword) != -1)  :
                        #check if it has special char  or it's thai language or it's stopwords
                            break;
                    else :
                        if (thaiword not in data.keys())  : #if first time
                            data[thaiword] = 1      #assight values
                            self.count += 1

                        else :   #else on
                            data[thaiword] += 1
                            self.count += 1

            else :

                sentence = self.sp(tweet)
                for word in sentence :

                    for badChar in self.specialChar :
                        if (  word.text.find(badChar) != -1  #find bad character in string
                                                       or word.pos_ in self.badPos  #find don't want pos pattern
                                                       or len(word.text) == 1  #char check
                                                       or word.text in self.stop_words
                                                       or word.text.find(keyword) != -1)  : #in stopword
                            break
                    else :
                        if (word.text not in data.keys() )  : #if first time
                            data[word.text] = 1  #assight values
                            self.count += 1
                        else :  #else on
                            data[word.text] += 1
                            self.count += 1

        items = list(data.items()) #convert dictionary to tuple
        items.sort(key=itemgetter(1), reverse=True) #sorting tumple with argument [1] is counted word

        tm = datetime.now()  #calculate now date time
        tm_rounded = pd.Series(tm).dt.round('1min')
        time = tm_rounded.at[0]   #rounding datetime to dd-mm-yyyy

        tempDF = pd.DataFrame(columns= ["word","count","date","range"] ) #create empty word
        for k in range(len(items)) :
            #add each items to pandas temp to save cache
            new_column = pd.Series([items[k][0], items[k][1], time,  "{},{}".format(since,until) ], index=tempDF.columns)
            tempDF = tempDF.append(new_column,ignore_index=True)
        tempDF.to_csv("{}/temp/{}_{}_{}.csv".format(os.getcwd(), keyword,since,until), index=False, mode="w") #save temp dataframe to cache file

        if plot :
            #if want to plot plot in bar Graph
            self.barPlot(items)

        if  (self.tester != None ) :
            self.tester.temp.emit(int(100))

        return items #retule result list of tulpe (word, count)

    def collectTrendData(self, listHashtag, lang="th", quantity=300, mode='a', timeAfter=True) :
        self.isValidSinceUntil(since, until)
        try :
            reader = pd.read_csv("twitterCrawler.csv")
            if (timeAfter != True ) :
                lastDateTime = reader["date"][1].split(" ")[0]
            else :
                lastDateTime = None
            print("Last Updation Data is :",lastDateTime)
        except :
            print("Error NO FOUND")
            lastDateTime=None
        for keyword in listHashtag :
            self.collectData(keyword,lang=lang,quantity=quantity, lastDateTime=lastDateTime, mode=mode )

    def collectData(self, keyword, lang="th", quantity=300, mode='w' , lastDateTime=None, until=None, result_type="recent") :
        ### collectData seaching keyword in twitter api , kept result in database csv file and return result in pandas dataframe type

        self.isValidSinceUntil(lastDateTime, until) #check it since and until is valid
        try :
            self.df = pd.read_csv("{}/data/{}/{}_{}.csv".format(os.getcwd(), self.fileNameTwitter, lastDateTime, until))
            #loading daatabase to pandas dataframe
        except FileNotFoundError :
            self.df = pd.DataFrame(columns= ["tweet","user","relateHashtag","date","place"] )
            #if not have one create empty pandas dataframe
        n = 0
        print("Searching Keyword : {}".format(keyword),lastDateTime, until)
        for tweet in tweepy.Cursor(self.api.search, q="{} -filter:retweets".format(keyword),
                                    count=30,
                                    since=lastDateTime,
                                    until=until,
                                    result_type=result_type,
                                    tweet_mode="extended",
                                    lang=lang).items() :
            #searching  with cursor in twitter
            entity_hashtag = tweet.entities.get("hashtags")  #get all string data
            hashtag = ""  #empty hashtag string
            for i in range(0,len(entity_hashtag)):
                hashtag = hashtag +"/"+entity_hashtag[i]["text"]  #add hashtag to string
            else :
                if (hashtag == "") :
                    hashtag = "/"+keyword
            try :
                sentence = tweet.retweeted_status.full_text #get string for retweet
            except :
                sentence = (tweet.full_text) #get string for main tweet
            sentence = self.emoji_pattern.sub(r'', sentence)
            sentence = sentence.lower()  #change to lower of string
            print(tweet.created_at ==  lastDateTime,tweet.created_at , lastDateTime)
            if (n > quantity or tweet.created_at ==  lastDateTime) :
                print(n, lastDateTime)
                break
            n += 1

            new_column = pd.Series([sentence, tweet.user.screen_name, hashtag, tweet.created_at, tweet.user.location ], index=self.df.columns)
            #add data to pandas dataframe
            self.df = self.df.append(new_column,ignore_index=True)
        self.df.to_csv("{}/data/{}/{}_{}.csv".format(os.getcwd(), self.fileNameTwitter, lastDateTime, until), index=False, mode=mode)
        #save database
        return self.df #return result

    def barPlot(self,data,rankNo=9) :
        import matplotlib as mpl
        print(":::PROCESS GRAPH ")
        #plot data tuple input to pie graph
        fp = mpl.font_manager.FontProperties(family="Sukhumvit set" ,size=14) #create thai  font
        label = [] #empty label , values, explode
        values = []
        explode = []
        count = 0
        print(data)
        plt.clf()
        for k in data :
            count += k[1]
        for k in range(rankNo) :
            explode.append(0.1)
            label.append(data[k][0])  #add to label list
            values.append(data[k][1]/count*100) #calculate percent

        x = np.arange(0,rankNo)
        ax = plt.gca(xticks=x)
        ax.set_xticklabels(label,rotation=10,fontproperties=fp )
        plt.bar(label,values,color='slateblue')
        plt.show()
        plt.clf()

    def geopyToPandas(self,keyword, since=None, until=None, worker=None) :
        ###convert keyword that in database to pandas dataframe with location , count
        ### worker is thread object to emit data
        self.isValidSinceUntil(since, until) #check  is since and until is valid
        if worker != None :
            self.worker_Location = worker  #set worker thread to attribute

        try:
            geocodeLocalBase = pd.read_csv("{}/temp/geocodeLocalBase.csv".format(os.getcwd())) #reading local GeoCoding database
            #read local Base Geocoder data if we have
        except FileNotFoundError:
            geocodeLocalBase = pd.DataFrame(columns= ["location","latitude","longitude"] )
            #if not found instace DataFrame
        try :

            return pd.read_csv("{}/temp/{}_{}_{}_map.csv".format(os.getcwd(), keyword, since, until)) #reading cache file

        except FileNotFoundError :
            #if not found
            reader = self.readingData(since=since, until=until) #reader is database
            save = pd.DataFrame(columns= ["location","latitude","longitude","count"] ) #save dataframe to  cached result to csv
            geolocator = Nominatim(user_agent="http") #instance geocoder
            dictLocate = dict() #create dict to collect freq
            count = 0

            for tweet in reader["place"] : #in dataframe col "place"

                if not pd.isna(tweet) :  #is not empty or NaN
                    tweet = tweet.lower()  #translate to lower char to minimize time  and dupicate name
                    boolValues = False #temp booleans
                    for badChar in self.badLocation :
                        #self.badLocation is location char that  is special char that exclude
                        if tweet.find(badChar) != -1 :
                            #if find bad character
                            boolValues = True #temp booleans to true  means find badchar
                            break
                    if  (re.search(self.emoji_pattern, tweet) != None) or boolValues   :
                        #if find emoji pattern  or speacial character
                        pass
                    elif tweet in dictLocate :
                        dictLocate[tweet] += 1  #counting
                    else :
                        dictLocate[tweet] = 1 #set start freq
                    count += 1

            for location in dictLocate :

                if (self.worker_Location != None ):
                    #if we included thread
                    self.progressLocation += (1/self.sizeOfWorkLocation)*100 #calculate increaseing progress bar
                    self.worker_Location.progress.emit(int(self.progressLocation)) #emit pyqtSignal to update
                try :
                    readerGeocodeLocal = geocodeLocalBase[geocodeLocalBase.location.str.match(location,case=False)]

                except :
                    pass

                if len(readerGeocodeLocal) > 0  :
                    #if find reader contain in local GeoCoding
                    for locationing, latitude, longitude in readerGeocodeLocal.itertuples(index=False) :
                        #in dataframe
                        locationing = locationing.lower() #convert to lower
                        if (locationing == location) :
                            new_column = pd.Series([locationing, latitude,longitude,dictLocate[locationing]], index=save.columns)
                            #loading cache data and append to pandas dataframe
                            save = save.append(new_column,ignore_index=True)
                            break
                    else :
                        try:
                            locationg = geolocator.geocode(location,timeout=10)
                            if locationg is not None :

                                new_column = pd.Series([location, locationg.latitude, locationg.longitude, dictLocate[location]], index=save.columns)
                                save = save.append(new_column,ignore_index=True)

                                new_column = pd.Series([location, locationg.latitude,locationg.longitude ], index=geocodeLocalBase.columns)
                                geocodeLocalBase = geocodeLocalBase.append(new_column, ignore_index=True)
                        except Exception as e:
                            print(e)

                else :
                    try:
                        locationg = geolocator.geocode(location,timeout=10)
                        if locationg is not None :

                            new_column = pd.Series([location, locationg.latitude, locationg.longitude, dictLocate[location]], index=save.columns)
                            save = save.append(new_column,ignore_index=True)

                            new_column = pd.Series([location, locationg.latitude,locationg.longitude ], index=geocodeLocalBase.columns)
                            geocodeLocalBase = geocodeLocalBase.append(new_column, ignore_index=True)
                    except Exception as e :
                        print(e)

        save.to_csv("{}/temp/{}_{}_{}_map.csv".format(os.getcwd(), keyword, since, until), index=False, mode="w")
        geocodeLocalBase.to_csv("{}/temp/geocodeLocalBase.csv".format(os.getcwd(), keyword), index=False, mode="w")

        return save

    def foliumPlotMarker(self, df) :
        self.mapvar = folium.Map(location=[50.358363, 7.614098],zoom_start=2, tiles="Stamen Terrain",) #create folium map
        self.dictLocate = dict() #create dict to collect freq
        self.count = 0
        for location, latitude, longitude, count in df.itertuples(index=False) :  #in dataframe col "place"
            #for in data frame
            if location in self.dictLocate :
                #if have already in dict  add
                self.dictLocate[location] += count
            else :
                #if not have
                self.dictLocate[location] = count
            self.count += 1

        if (len(self.dictLocate) > 0 ) :  #if have data
            #if have location then
            self.average = self.count/len(self.dictLocate) #calculate average from counted values

            for location, latitude, longitude, count in df.itertuples(index=False) :  #in keys from dict

                #recognize color by them fequency that below or more than average
                if self.dictLocate[location] > self.average*3/2 :
                    self.color = 'red'
                elif self.dictLocate[location] > self.average :
                    self.color = 'orange'
                elif self.dictLocate[location] > self.average*2/3  :
                    self.color = 'lightgreen'
                else :
                    self.color = 'green'

                folium.Marker(location=[latitude, longitude], icon=folium.Icon(color=self.color)).add_to(self.mapvar) #plot each location that found to map
        self.mapvar.save("hsa.html")
        return self.mapvar

    def isRepeatChar(self, string ) :
        ### check if string is same char and repeat char
        firstChar = string[0] #collect first character
        for char in string :
            #for range in string
            if char != firstChar :
                #if char is not same as first string
                return False
        else :
            #if char have repeate then return
            return True

    def datecheck(self,keyword, since, until) :
        ### method that checking date that not include in database and try searching
        self.isValidSinceUntil(since, until) #check if valid since and until
        d1 = datetime.strptime(since, "%Y-%m-%d") #convert since to datetime object
        d2 = datetime.strptime(until, "%Y-%m-%d") #convert until to datetime object
        diff_days = abs((d2 - d1).days) #cacluate different of since, until
        for k in range(diff_days+1) :
            d3 = d1+timedelta(days=k) #increasing dataframe
            try :
                reader = self.readingData(d3.strftime("%Y-%m-%d"), (d3+timedelta(days=1)).strftime("%Y-%m-%d"))
                #reading database to pandas dataframe
                if len(reader[reader.relateHashtag.str.contains(keyword.replace("#",""),case=False) &  reader.date.str.contains(d3.strftime("%Y-%m-%d"),case=False)]) >= 50 :
                    #if have more data in database less than 50
                    print("found enough data in date",d3.strftime("%Y-%m-%d"))
                else :
                    self.collectData(keyword, lastDateTime=d3.strftime("%Y-%m-%d"), until=(d3+timedelta(days=1)).strftime("%Y-%m-%d"),quantity=100)
                    #collecting data to database in increased date quantity
                    self.collectData(keyword, lastDateTime=d3.strftime("%Y-%m-%d"), until=(d3+timedelta(days=1)).strftime("%Y-%m-%d"),quantity=50, lang="en")
                    #collecting data to database in increased date quantity
                    print("need to find case#1",d3.strftime("%Y-%m-%d"),(d3+timedelta(days=1)).strftime("%Y-%m-%d"))

            except FileNotFoundError :
                #if not fond that date in database
                self.collectData(keyword, lastDateTime=d3.strftime("%Y-%m-%d"), until=(d3+timedelta(days=1)).strftime("%Y-%m-%d"),quantity=100)
                #collecting data to database in increased date quantity
                self.collectData(keyword, lastDateTime=d3.strftime("%Y-%m-%d"), until=(d3+timedelta(days=1)).strftime("%Y-%m-%d"),quantity=50, lang="en")
                #collecting data to database in increased date quantity
                print("need to find case#2",d3.strftime("%Y-%m-%d"),(d3+timedelta(days=1)).strftime("%Y-%m-%d"))

    def readingData(self, since=None, until=None) :
        #### reading data from database  and return to pandas data
        self.df = pd.DataFrame(columns= ["tweet","user","relateHashtag","date","place"] ) #create empty dataframe

        if not "data" in os.listdir() :
            #if no database file in list create directory to support database
            os.mkdir("{}/data".format(os.getcwd()))
            os.mkdir("{}/data/{}".format(os.getcwd(), self.fileNameTwitter))

        print(since, until,"::::::::::::")
        if (since == None and until == None ) :
            
            cacheList = os.listdir("{}/data/twitterCrawler".format(os.getcwd()))
            for each_file in cacheList :

                df_temp = pd.read_csv("{}/data/{}/{}_{}.csv".format(os.getcwd(), self.fileNameTwitter, d3.strftime("%Y-%m-%d"), (d3+timedelta(days=1)).strftime("%Y-%m-%d")))
                #reading data from increased date  and
                frame = [self.df, df_temp] #concat dataframe to self.df
                self.df = pd.concat(frame)

            return self.df

        elif (since != None and until == None ) :
            d1 = datetime.strptime(since, "%Y-%m-%d")
        elif (since == None and until != None ) :
            d2 = datetime.strptime(until, "%Y-%m-%d")
        else :
            d1 = datetime.strptime(since, "%Y-%m-%d")
            d2 = datetime.strptime(until, "%Y-%m-%d")

        diff_days = abs((d2 - d1).days) #calculate different of since and date

        for k in range(diff_days) :
            #in range of different date time
            d3 = d1+timedelta(days=k) #increasing date  to d3
            try :
                df_temp = pd.read_csv("{}/data/{}/{}_{}.csv".format(os.getcwd(), self.fileNameTwitter, d3.strftime("%Y-%m-%d"), (d3+timedelta(days=1)).strftime("%Y-%m-%d")))
                #reading data from increased date  and
                frame = [self.df, df_temp] #concat dataframe to self.df
                self.df = pd.concat(frame)
            except FileNotFoundError :
                #if not found excactly date
                print("need to find case#3",d3.strftime("%Y-%m-%d"),(d3+timedelta(days=1)).strftime("%Y-%m-%d"))
        return self.df #return result after concat

    def isValidSinceUntil(self, since, until) :
        #### check if since and until is correct type and and return true , else raise Exception
        if  (since!=None and until!=None) :
            #if not None input
            d1 = datetime.strptime(since, "%Y-%m-%d") #convert since to datetime object
            d2 = datetime.strptime(until, "%Y-%m-%d") #convert until to datetime object
            if (d2-d1).days <= 0 : #if different of date is negative means since is less than until
                raise Exception("Insert Again Since is new than Until")  #raise exception
            else :
                return True #return if since date is correctly
        else :
            return True #return if none type










if __name__ == "__main__" :
    start = time.time()
    app = Trendy()
    #app.datecheck("โควิด", "2021-03-21", "2021-03-28")

    #x = app.foliumPlot("โควิด","2021-03-21", "2021-03-31")
    #x.save("smt.html")
    #app.foliumPlotMarker(x)
    #print(app.findAndCombineSentiment("โควิด", "2021-03-21", "2021-03-31"))
    app.validSinceUntil("2021-03-31", "2021-03-21")
    print("::::: Using Time = ", time.time() - start)





    #app.collectData("#covid", lang="en", quantity=100, mode="w"
    #app.datecheck("โควิด","2021-01-11","2021-02-18")
    #print(app.sentimenTweet("BTC"))

    #for k in app.readDay("2021-03-19", "2021-03-22")['date'] :
        #print(k)
    start = time.time()
    #data = app.findAndCombineLocation("covid","2021-03-16", "2021-03-26")

    #print(data)
#app.collectData("#โควิด", lang="th", quantity=50,mode='w')
#app.searchHashtag("เคเอฟซีมายบอกซ์มายคริส")
#data = app.analyze("COVID",lang="th", quantity=100)
