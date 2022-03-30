# เขียนโดย นาย วรรณพงษ์  ภัททิยไพบูลย์
# ใช้ประกอบบทความใน python3.wannaphong.com
# cc-by 3.0 Thai Sentiment Text https://github.com/wannaphongcom/lexicon-thai/tree/master/ข้อความ/
# อ่านบทความได้ที่ https://python3.wannaphong.com/2017/02/ทำ-sentiment-analysis-ภาษาไทยใน-python.html

from nltk import NaiveBayesClassifier as nbc
from pythainlp.tokenize import word_tokenize
import codecs
from itertools import chain
import os
import pickle
import nltk
from textblob import TextBlob
import re
import pickle
import time
import deepcut


class Sentiment :

    def __init__(self) :

        if "config" not in os.listdir() : #checking directory config in list
            os.mkdir("config") #if don't have create directory "config"

        with codecs.open('{}/config/pos.txt'.format(os.getcwd()), 'r', "utf-8") as f:
        #open positive word in config file
            lines = f.readlines() #read all data  in file
        listpos=[e.strip() for e in lines]
        del lines
        f.close() #close file

        # neg.txt
        with codecs.open('{}/config/neg.txt'.format(os.getcwd()), 'r', "utf-8") as f:
        #open negative word in config file
            lines = f.readlines() #read all data  in file
        listneg=[e.strip() for e in lines]
        f.close() #close file

        with codecs.open('{}/config/neu.txt'.format(os.getcwd()), 'r', "utf-8") as f:
        #open neutral word in config file
            lines = f.readlines() #read all data  in file
        listneu=[e.strip() for e in lines]
        del lines
        f.close()

        pos1=['pos']*len(listpos) #create empyty "pos" in list equal quantity of  listpos
        neg1=['neg']*len(listneg) #create empyty "neg" in list equal quantity of  listneg
        neu1=['neu']*len(listneu) #create empyty "neu" in list equal quantity of  listneu

        training_data = list(zip(listpos,pos1)) + list(zip(listneg,neg1)) + list(zip(listneu, neu1)) #create pair of word : result

        self.vocabulary = set(chain(*[word_tokenize(i[0].lower()) for i in training_data]))
        try :
            with open('{}/config/sentiment.pkl'.format(os.getcwd()), 'rb') as handle:
            #if find sentiment.pkl
                self.classifier = pickle.load(handle)
                #load pickled
        except :
            #else train new data in config
            self.train()



    def train(self ) :

        with codecs.open('{}/config/pos.txt'.format(os.getcwd()), 'r', "utf-8") as f:
            lines = f.readlines()
        listpos=[e.strip() for e in lines]
        del lines
        f.close() # ปิดไฟล์
        # neg.txt
        with codecs.open('{}/config/neg.txt'.format(os.getcwd()), 'r', "utf-8") as f:
            lines = f.readlines()
        listneg=[e.strip() for e in lines]
        f.close() # ปิดไฟล์

        with codecs.open('{}/config/neu.txt'.format(os.getcwd()), 'r', "utf-8") as f:
            lines = f.readlines()
        listneu=[e.strip() for e in lines]
        del lines
        f.close()

        pos1=['pos']*len(listpos)  #create empyty "pos" in list equal quantity of  listpos
        neg1=['neg']*len(listneg)  #create empyty "neg" in list equal quantity of  listpos
        neu1=['neu']*len(listneu)  #create empyty "neu" in list equal quantity of  listpos
        training_data = list(zip(listpos,pos1)) + list(zip(listneg,neg1)) + list(zip(listneu, neu1)) #create pair of word : result
        self.vocabulary = set(chain(*[word_tokenize(i[0].lower()) for i in training_data]))
        feature_set = [({i:(i in word_tokenize(sentence.lower())) for i in self.vocabulary},tag) for sentence, tag in training_data]
        self.classifier = nbc.train(feature_set)

        with open('{}/config/sentiment.pkl'.format(os.getcwd()), 'wb') as handle:
                pickle.dump(self.classifier, handle)

    def sentimentTH(self, keyword) :
        start = time.time()
        tokenized = word_tokenize(keyword)
        #featurized_test_sentence =  {i:(i in tokenized) for i in self.vocabulary}
        featurized_test_sentence = dict()
        for i in self.vocabulary :
            if i in tokenized :
                featurized_test_sentence[i] = True
            else :
                featurized_test_sentence[i] = False

        featurized_test_sentence["ไม่"] = False
        for k in range(len(tokenized)) :
            if (tokenized[k] == "ไม่") :
                if (tokenized[k+1] in featurized_test_sentence) :
                    featurized_test_sentence[tokenized[k+1]] = not (featurized_test_sentence[tokenized[k+1]])
        return self.classifier.classify(featurized_test_sentence)

    def sentimentEN(self, keyword) :
        analysis = TextBlob(keyword)
        if analysis.sentiment[0]>0:
           return "pos"
        elif analysis.sentiment[0]<0:
           return "neg"
        else:
           return "neu"


    def sentiment(self, keyword) :

        m = re.search("[ก-๛]", keyword)
        if m != None :
            #print("thai : ", keyword)
            return self.sentimentTH(keyword)
        else :
            #print("eng : ", keyword)
            return self.sentimentEN(keyword)


if __name__ == "__main__" :
    start = time.time()
    s1 =  Sentiment()


    print("this")
    print(s1.sentiment("สวัสดี"))
    print(time.time()-start)
    print(s1.sentiment("หรอไอสัส"),"ไอสัสไม่ใช่ละ")

    print(s1.sentiment("หนังนี้ก็สนุก"))
    print(s1.sentiment("หนังเรื่องนี้ไม่ดีเลย"))
    print(s1.sentiment("จากการสำรวจพบว่า"))
    print(s1.sentiment("And I say, Yes, I feel wonderful tonight."))
    print(s1.sentiment(" The mouse will not fully charge. Also the mouse buttons have lateral movement making them overlap at times. This makes one mouse click actuate the other. Unacceptable at any price point let alone $150."))
    print(s1.sentiment("ตัดมาประยุทธ ให้ท้องที่อายัดทรัพย์ให้ได้ปีละ 5,000 ล้านอิห่าส่วยแบบ ไทยแลนด์ 4.0"))
    print(s1.sentiment("ประยุทธ์"))
