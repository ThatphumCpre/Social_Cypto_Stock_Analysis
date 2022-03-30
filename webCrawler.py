import bs4
import requests
from pysbd.utils import PySBDFactory
import spacy
from pythainlp.tokenize import word_tokenize
from datetime import datetime
from datetime import timedelta
import pandas as pd
from pythainlp.corpus.common import thai_words
from pythainlp import Tokenizer
from pythainlp.corpus import thai_stopwords
import nltk
from nltk.corpus import stopwords
import re
import matplotlib as mpl
import matplotlib.pyplot as plt
import emoji
import matplotlib as mpl
import numpy as np
import pythainlp.util
import os
import deepcut
import urllib.request
from sentiment import Sentiment
from operator import itemgetter
import pickle



class WebCrawler :

    def __init__(self) :
        tm = datetime.now()
        tm_rounded = pd.Series(tm).dt.round('1min')
        print(tm_rounded)

        #progress bar status of trenword
        self.count = 0
        self.progressTrend = 0
        self.sizeOfWork = 0

        #progressbar status and qthread objt worker of sentiment
        self.progressSetiment = 0
        self.sizeOfWorkSentiment = 0
        self.worker_sentiment = None

        self.sp = spacy.load("en_core_web_sm") #load tokenize en
        self.fileNameTwitter = "webCrawler" #variable name of file collecting
        self.count = 0
        self.progressTrend = 0
        self.progressSetiment = 0
        self.jobDoneList = set() #set of link that we done
        self.stop_words = set(stopwords.words("english")) #stop owrd
        self.specialChar = [":","/","#","@","?", '&', ';', "…",'<', '>','{','}','©','=','*','[',']'] #don't deserve char
        self.thai_stopwords = set(thai_stopwords())
        self.emoji_pattern = re.compile("["
                                    u"\U0001F600-\U0001F64F"  # emoticons
                                    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                    u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                    "]+", flags=re.UNICODE)
        self.badPos = ["AUX","ADP","SCONJ", "DET","PART","CCONJ","NUM","PROPN"]
        self.specialWord = {"<", ">", ";", "{", "}",':','@'} #collect char that must not in sentence
        self.category = list() #data that use collecting result

        try :
            tm = datetime.now()
            #self.df = self.df.drop_duplicates(subset=['website'], keep='last')
            self.df = pd.read_csv("{}/data/webCrawler/{}.csv".format(os.getcwd(), tm.strftime("%Y-%m-%d")))
            print("find")

        except :
            self.df = pd.DataFrame(columns= ["head","date","website","domain","context"] )

    def __sorted(self) :
        #delete dupicate and sort data
        self.category.sort()  #sorting
        temp = []  #create temp to collect
        for news in self.category :
            if news not in temp :
                temp.append(news)  #if not dupicate then append
        self.category = temp #replace non-dupicate

    def getTrendWordData(self, keyword, since=None, until=None) :
        ### getTrendData is analyze trend word of web handle exception and cache load
        ### get argument keyword to get trend word keyword hashtag with tuple of (word,count)
        print(since,until, keyword, ":::::::::::::::::::FDAFDSF:::::")
        try :
            temp = keyword
            reader = pd.read_csv("{}/temp/{}_web_{}_{}.csv".format(os.getcwd(), keyword, since, until)) #try reading data cache
            data = list()
            readingSince, readingUntil = reader["range"][1].split(",")

            if  (readingSince == since and readingUntil == until) or (readingSince == None and readingUntil  == None ) :
                for index, col in reader.iterrows() :
                    #if have append to data
                    data.append((col["word"],col["count"]))
                return data
            else :
                #if don't have same date
                return self.analyze(keyword, since=since, until=until)

        except FileNotFoundError:
            #else if FileNotFoundError
            if not "temp" in os.listdir() :
                os.mkdir("temp")
            try :
                return self.analyze(keyword, since=since, until=until)  #analyze trending list
            except :
                return self.analyze(keyword, since=since, until=until)

    def search(self,keyword, since=None, until=None  ) :
        try :
            reader = pd.read_csv("{}/temp/{}_web_{}_{}.csv".format(os.getcwd(), keyword, since, until))
            data = []
            readingSince, readingUntil = reader["range"][1].split(",")
            print((readingSince >= since and readingUntil <= until) , (readingSince == None and readingUntil  == None ))
            if  (readingSince == since and readingUntil == until) or (readingSince == None and readingUntil  == None ) :
                for index, col in reader.iterrows() :
                    data.append((col["word"],col["count"]))
                self.barPlot(data)
            elif(len(data) == 0) :
                self.analyze(keyword, since=since, until=until)

        except :
            print("hi")
            if not "temp" in os.listdir() :
                os.mkdir("temp")
            self.analyze(keyword, since=since, until=until)

    def view(self)  :
        print("\n\n========= NEWS TODAY  ===========")
        for news in self.category :
            print(news)

    def analyze(self, keyword, since=None, until=None, plot=True, worker=None) :
        ### analyze() is method that input argument with keyword

        if worker != None :
            self.tester = worker

        print(since,until, keyword, ":::::::::::::::::::FDAFDSF:::::")

        keyword = keyword.lower()
        data = dict()
        words = set(thai_words())           #create set of nlp data
        words.add(keyword)           #add keyword to data set
        custom_tokenizer = Tokenizer(words) #create new tokenize from custom dataset
        reader = self.readingData(since, until)
        if (since == None and until == None  ) :
            df = reader[reader['head'].str.contains(keyword,case=False)]
        elif (since != None and until == None) :
            df = reader[reader['date'].str.contains(since,case=False) & reader['head'].str.contains(keyword,case=False) ]
        elif (since != None and until != None) :
            df = reader[ (reader['date'] >= since ) & (reader['date'] <= until) & (reader['head'].str.contains(keyword,case=False) )]
        if (len(df) == 0 ) :
            print("Didn't Found Keyword in data")

        self.sizeOfWork = len(df)
        print(df)

        for head,date,website,domain,context in df.itertuples(index=False):
            print(domain)
            if  (self.tester != None ) :
                #if had qthread object in attribuye
                self.progressTrend += (1/self.sizeOfWork)*50 #calculate % in headlines
                self.tester.temp.emit(int(self.progressTrend)) #emit signal to update progress batr

            if domain not in data : #frequency counting each domain
                data[domain] = 1
            else :
                data[domain] +=1

        if (since == None and until == None  ) :
            df = reader[reader['context'].str.contains(keyword,case=False,na=False)]
        elif (since != None and until == None) :
            df = reader[reader['date'].str.contains(since,case=False) & reader['context'].str.contains(keyword,case=False,na=False) ]
        elif (since != None and until != None) :
            df = reader[ (reader['date'] >= since ) & (reader['date'] <= until) & (reader['context'].str.contains(keyword,case=False,na=False) )]

        #reading context
        print(df)
        self.sizeOfWork = len(df)
        for head,date,website,domain,context in df.itertuples(index=False):

            if  (self.tester != None ) :
                #if had q thread object in attribute
                self.progressTrend += (1/self.sizeOfWork)*50 #calculate % in context
                self.tester.temp.emit(int(self.progressTrend)) #emit signal to update progress bar

            if domain not in data : #frequency counting each domain  that found
                data[domain] = 1
            else :
                data[domain] +=1


        items = []
        for key, value in data.items():
            temp = (key,value)
            items.append(temp)
        items.sort(key=itemgetter(1), reverse=True)  #sorting

        tm = datetime.now()
        tm_rounded = pd.Series(tm).dt.round('1min')
        time = tm_rounded.at[0]


        tempDF = pd.DataFrame(columns= ["word","count","date","range"] )
        for k in range(len(items)) :
            new_column = pd.Series([items[k][0], items[k][1], time, "{},{}".format(since,until) ], index=tempDF.columns)
            tempDF = tempDF.append(new_column,ignore_index=True)
        tempDF.to_csv("{}/temp/{}_web_{}_{}.csv".format(os.getcwd(), keyword, since, until), index=False, mode="w")
        #save items to cache
        print(items)
        if (plot) :
            self.barPlot(items,rankNo=len(items))

        return items #return result

    def sentimenTweet(self, keyword, since=None, until=None, worker=None ) :
        if worker != None :
            self.worker_sentiment = worker

        try :
            with open('{}/temp/{}_web_{}_{}.pkl'.format(os.getcwd(),keyword, since, until), 'rb') as handle:
            #if find .pkl and cache loading of sentiment result
                result = pickle.load(handle)
        except :

            sentiment = Sentiment()
            reader = self.readingData(since=since, until=until)
            if (since == None and until == None  ) :
                df = reader[reader['head'].str.contains(keyword,case=False)]
            elif (since != None and until == None) :
                df = reader[reader['date'].str.contains(since,case=False) & reader['head'].str.contains(keyword,case=False) ]
            elif (since != None and until != None) :
                print(   (reader['date'] <= until ))
                df = reader[ (reader['date'] >= since ) & (reader['date'] <= until) & (reader['head'].str.contains(keyword,case=False) )]
            if (len(df) == 0 ) :
                print("Didn't Found Keyword in data")
            pos, neg, neu = 0, 0, 0
            self.sizeOfWorkSentiment = len(df)

            for k in df['head'] :
                result = sentiment.sentiment(k)

                if self.worker_sentiment != None :
                    self.progressSetiment += (1/self.sizeOfWorkSentiment)*100
                    self.worker_sentiment.progress.emit(self.progressSetiment)

                print(result)
                #frequency counting
                if result == "neg" :
                    neg += 1
                elif result == "pos" :
                    pos += 1
                else :
                    neu += 1

            if (since == None and until == None  ) :
                df = reader[reader['context'].str.contains(keyword,case=False,na=False)]
            elif (since != None and until == None) :
                df = reader[reader['date'].str.contains(since,case=False) & reader['context'].str.contains(keyword,case=False,na=False) ]
            elif (since != None and until != None) :
                print(   (reader['date'] <= until ))
                df = reader[ (reader['date'] >= since ) & (reader['date'] <= until) &( reader['context'].str.contains(keyword,case=False,na=False) )]

            for k in df['head'] :
                result = sentiment.sentiment(k)
                if result == "neg" :
                    neg += 1
                elif result == "pos" :
                    pos += 1
                else :
                    neu += 1

            print(pos, neu, neg)
            result = {"Positive":pos, "Neutral":neu, "Negative":neg}
            with open('{}/temp/{}_web_{}_until.pkl'.format(os.getcwd(), keyword, since, until), 'wb') as handle:
                    pickle.dump(result, handle)

        return result

    def analyzeEN(self, domain, mode='w', max_ring=2, now_ring=None, domainName=None) :
        ### analyzeEN() from link domain arugument that show in state LINK->HEADLINE->Context
        self.head = True
        self.context = False
        tm = datetime.now()
        tm_rounded = pd.Series(tm).dt.round('1min')
        #print("[{}] : {} ".format(tm,domain))

        if (now_ring == None ) :
            #initial cases
            now_ring = max_ring #set recursion
            domainName = ""
            temp = domain.split('/')

            #html link check
            if len(temp) > 3 :
                for k in range(3) :
                    domainName += temp[k]+'/'
            else :
                return False

        if (now_ring == 0 or domain.find(domainName) == -1 or domain in self.jobDoneList ):
            #print(domain, "deny")
            return 0
        spiderLinks = set()

        headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 OPR/67.0.3575.137"}
        try :
            requested = requests.get(domain,headers=headers)  #request to domain call
        except requests.exceptions.InvalidSchema :
            return False
        except requests.exceptions.ConnectionError :
            return False
        except :
            return False

        file = open("scape.txt", "w")  #write to file
        html_page = bs4.BeautifulSoup(requested.text, "html.parser") #make more easier to read
        file.write(html_page.prettify()) #write an easier format
        file.close() #close file

        file = open("scape.txt", "r")  #read file that write
        data = file.readlines()
         #load data set for english
        head = ""
        context = ""
        for lineNumber in range(len(data)) : #read all data form all readlines
            line = data[lineNumber].strip()  #read line

            if ( line.find("""href=""") != -1   ) :
                #if found link
                #if it's a main link not ADs and It's Tittle Class
                if (self.head and self.context and head != "") :
                    #found all element and find next href then save and re new
                    tm = datetime.now()
                    tm_rounded = pd.Series(tm).dt.round('1min')
                    self.category.append(data[lineNumber ].strip())
                    new_column = pd.Series([head, tm_rounded.at[0], domain, domainName, context ], index=self.df.columns)
                    self.df = self.df.append(new_column,ignore_index=True)
                    self.jobDoneList.add(domain)
                    #print(head,tm_rounded.at[0],domain, domainName, sentence )
                    if (domain != domainName) :
                        pass

                at = line.find("""href=""")+5
                count = 0
                str = ""
                context = ""

                #collecting href with none RE
                while (count <2 and at < len(line)) :
                    if (line[at] == '"' or line[at] == '?') :
                        count += 1
                    else :
                        str += line[at]
                    at += 1
                if (len(str)<3 ) :
                    pass

                #string href type syntax pattern to real html link
                elif str[0] == '/' and str[1] =='/' :
                    str = "https:"+str
                    spiderLinks.add(str)
                    if (now_ring == max_ring ) :
                        domain = str
                elif str.find("www") != -1 :
                    spiderLinks.add(str)
                    if (now_ring == max_ring ) :
                        domain = str
                elif str[0] == '.' :
                    spiderLinks.add((domainName+str[2:]))
                    if (now_ring == max_ring ) :
                        domain = (domainName+str[2:])
                elif str[0] == '/' :
                    spiderLinks.add((domainName+str[1:]))
                    if (now_ring == max_ring ) :
                        domain = (domainName+str[1:])
                else :
                    spiderLinks.add(str)
                    if (now_ring == max_ring ) :
                        domain = str

                #change state to find headline
                self.head = True
                self.context = False

            if self.head  and not self.context :
            #state to save headline
                for word in self.specialChar : #for in special word
                    if ( data[lineNumber].strip().find(word) != -1 ) : #if in then break
                        break;
                else :
                    #print(line)
                    sentence = self.sp(data[lineNumber].strip()) #else tokenize
                    if (len(sentence) > 6 ) :  #if more than 4 word then append
                        head=sentence
                        self.context = True #change state to find context


            elif self.context and self.head :
            #state to save context
                for word in self.specialChar : #for in special word
                    if ( data[lineNumber].strip().find(word) != -1 ) : #if in then break
                        break
                else :
                    #print(line)
                    sentence = self.sp(data[lineNumber].strip())
                    if (len(sentence) > 6 ) :
                        context += data[lineNumber ].strip()




        print(len(self.jobDoneList))
        for link in spiderLinks :
            #recursion case
            self.analyzeEN(link, now_ring=now_ring-1, max_ring=max_ring, domainName=domainName)

        if(now_ring >= max_ring) :
            #if first layer of recursion done
            self.jobDoneList = set()
            print("drop down column")
            if not "data" in os.listdir() :
                os.mkdir("{}/data".format(os.getcwd()))
            if "webCrawler" not in os.listdir("{}/data".format(os.getcwd())) :
                os.mkdir("{}/data/{}".format(os.getcwd(), self.fileNameTwitter))
            tm = datetime.now()
            #self.df = self.df.drop_duplicates(subset=['website'], keep='last')
            self.df.to_csv("{}/data/webCrawler/{}.csv".format(os.getcwd(), tm.strftime("%Y-%m-%d")), index=False, mode=mode)
            self.__sorted()

    def analyzeTH(self, domain, mode='w', max_ring=2, now_ring=None, domainName=None) :
        ###this method searching  domian that correspond and find headline context and website with recursion count with max_ring argument
        ##same algorithm as analyzeEN() but change tokenize and number of word count

        self.head = False
        self.context = False
        tm = datetime.now()
        tm_rounded = pd.Series(tm).dt.round('1min')
        print("[{}] : {} ".format(tm,domain))

        if (now_ring == None ) :
            self.sp = spacy.load("en_core_web_sm")
            now_ring = max_ring
            domainName = ""
            temp = domain.split('/')
            if len(temp) > 3 :
                for k in range(3) :
                    domainName += temp[k]+'/'
            else :
                return None

        if (now_ring == 0 or domain.find(domainName) == -1 or domain in self.jobDoneList ):
            print(domain, "deny")
            return False
        else :
            self.jobDoneList.add(domain)
        spiderLinks = set()

        headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 OPR/67.0.3575.137"}
        try :
            requested = requests.get(domain,headers=headers)  #request to domain call
        except :
            return False

        file = open("scape.txt", "w")  #write to file
        html_page = bs4.BeautifulSoup(requested.text, "html.parser") #make more easier to read
        file.write(html_page.prettify()) #write an easier format
        file.close() #close file

        file = open("scape.txt", "r")  #read file that write
        data = file.readlines()
         #load data set for english
        head = ""
        context = ""
        for lineNumber in range(len(data)) : #read all data form all readlines
            line = data[lineNumber].strip()  #read line

            if ( line.find("""href=""") != -1   ) :
                #if it's a main link not ADs and It's Tittle Class
                if (self.head and self.context and head != "") :
                    tm = datetime.now()
                    tm_rounded = pd.Series(tm).dt.round('1min')
                    self.category.append(data[lineNumber ].strip())
                    new_column = pd.Series([head, tm_rounded.at[0], domain, domainName, context ], index=self.df.columns)
                    self.df = self.df.append(new_column,ignore_index=True)
                    print(head,tm_rounded.at[0],domain, domainName, sentence )
                    if (domain != domainName) :
                        pass
                        #self.jobDoneList.add(domain)

                at = line.find("""href=""")+5
                count = 0
                str = ""
                context = ""


                while (count <2 and at < len(line)) :
                    if (line[at] == '"' or line[at] == '?') :
                        count += 1
                    else :
                        str += line[at]
                    at += 1
                if (len(str)<3 ) :
                    pass
                elif str[0] == '/' and str[1] =='/' :
                    str = "https:"+str
                    spiderLinks.add(str)
                    if (now_ring == max_ring ) :
                        domain = str
                elif str.find("www") != -1 :
                    spiderLinks.add(str)
                    if (now_ring == max_ring ) :
                        domain = str
                elif str[0] == '.' :
                    spiderLinks.add((domainName+str[2:]))
                    if (now_ring == max_ring ) :
                        domain = (domainName+str[2:])
                elif str[0] == '/' :
                    spiderLinks.add((domainName+str[1:]))
                    if (now_ring == max_ring ) :
                        domain = (domainName+str[1:])
                else :
                    spiderLinks.add(str)
                    if (now_ring == max_ring ) :
                        domain = str


                self.head = True
                self.context = False

            if self.head  and not self.context :
                for word in self.specialChar : #for in special word
                    if ( data[lineNumber].strip().find(word) != -1 ) : #if in then break
                        break;
                else :
                    sentence = self.sp(data[lineNumber ].strip()) #else tokenize
                    if (len(sentence) > 5 ) :  #if more than 4 word then append
                        head=sentence
                        self.context = True


            elif self.context and self.head :
                for word in self.specialChar : #for in special word
                    if ( data[lineNumber].strip().find(word) != -1 ) : #if in then break
                        break
                else :
                    sentence  = pythainlp.tokenize.word_tokenize(data[lineNumber].strip(), engine='deepcut') #tokenize

                    if (' ' in sentence ) :
                        sentence.remove(' ')
                    if (len(sentence) > 5 ) :
                        context += data[lineNumber].strip()



        print(spiderLinks)
        for link in spiderLinks :
            self.analyzeTH(link, now_ring=now_ring-1, max_ring=max_ring, domainName=domainName)

        if(now_ring >= max_ring) :
            self.jobDoneList = set()
            print("drop down column")
            if not "data" in os.listdir() :
                os.mkdir("{}/data".format(os.getcwd()))
            if "webCrawler" not in os.listdir("{}/data".format(os.getcwd())) :
                os.mkdir("{}/data/{}".format(os.getcwd(), self.fileNameTwitter))
            tm = datetime.now()
            #self.df = self.df.drop_duplicates(subset=['website'], keep='last')
            self.df.to_csv("{}/data/webCrawler/{}.csv".format(os.getcwd(), tm.strftime("%Y-%m-%d")), index=False, mode=mode)
            self.__sorted()

    def searchWord(self, keyword) :
        result = []
        for news in self.category :
            if (news.find(keyword) != -1 ) :
                result.append(news)
        return result

    def barPlot(self,data,rankNo=3) :
        print(":::PROCESS GRAPH ")
            #plot data tuple input to pie graph
        fp = mpl.font_manager.FontProperties(family="Sukhumvit set" ,size=14) #create thai  font
        label = [] #empty label , values, explode
        values = []
        explode = []
        count = 0
        for k in data :
            count += k[1]
        for k in range(rankNo) :
            if (k==len(data)) :
                break;
            explode.append(0.1)
            label.append(data[k][0])  #add to label list
            values.append(data[k][1]/count*100) #calculate percent

        x = np.arange(0,rankNo)
        ax = plt.gca(xticks=x)
        ax.set_xticklabels(label,rotation=10,fontproperties=fp )
        plt.bar(label,values,color='slateblue')
        plt.show()

    def readingData(self, since=None, until=None) :

        self.df = pd.DataFrame(columns= ["head","date","website","domain","context"] )
        if not "data" in os.listdir() :
            os.mkdir("{}/data".format(os.getcwd()))
            os.mkdir("{}/data/{}".format(os.getcwd(), self.fileNameTwitter))

        if (since == None and until == None ) :
            for each_file in os.listdir("{}/data/{}".format(os.getcwd(), self.fileNameTwitter)) :
                print(each_file)
                df_temp = pd.read_csv("{}/data/{}/{}".format(os.getcwd(), self.fileNameTwitter, each_file))
                frame = [self.df, df_temp]
                self.df = pd.concat(frame)
            return self.df

        elif (since != None and until == None ) :
            d1 = datetime.strptime(since, "%Y-%m-%d")
        elif (since == None and until != None ) :
            d2 = datetime.strptime(until, "%Y-%m-%d")
        else :
            d1 = datetime.strptime(since, "%Y-%m-%d")
            d2 = datetime.strptime(until, "%Y-%m-%d")

        diff_days = abs((d2 - d1).days)
        for k in range(diff_days+1) :
            d3 = d1+timedelta(days=k)
            try :
                print("{}/data/{}/{}.csv".format(os.getcwd(), self.fileNameTwitter, d3.strftime("%Y-%m-%d")))
                df_temp = pd.read_csv("{}/data/{}/{}.csv".format(os.getcwd(), self.fileNameTwitter, d3.strftime("%Y-%m-%d")))
                frame = [self.df, df_temp]
                self.df = pd.concat(frame)
            except FileNotFoundError :
                print("need to find case#3",d3.strftime("%Y-%m-%d"),(d3+timedelta(days=1)).strftime("%Y-%m-%d"))
        return self.df

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

if __name__ == "__main__"  :
    app = WebCrawler()
    list =["https://apnews.com/",
            "https://news.google.com/topstories?hl=en-US&gl=US&ceid=US:en",
            "https://www.nationthailand.com","https://www.nbcnews.com",
            "https://www.nytimes.com"]
    listTH = ["https://www.sanook.com/news/",
                "https://www.thairath.co.th/news",
                "https://www.thairath.co.th/news",
                "https://www.komchadluek.net"]
    #app.analyzeEN("https://www.bangkokpost.com",mode='w')
    #for k in list :
    app.analyzeEN("https://www.independent.co.uk/", mode='w')
    #for k in list :
    #app.analyzeEN("https://abcnews.go.com/Politics/kim-janey-sworn-1st-black-1st-woman-mayor/story?id=76650043&cid=clicksource_4380645_16_post_hero_bsq_hed",max_ring=1,mode='w')
    print(app.readingData())
    #print(":::::")
    #print(app.sentimenTweet("covid"))
    #app.view()
    #app.search("โควิด", since="2021-01-25", until="2021-01-26")
