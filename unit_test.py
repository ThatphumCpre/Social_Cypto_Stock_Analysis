import unittest
from twitterCrawler import Trendy
from sentiment import Sentiment
from biTools import Buisy
from webCrawler  import WebCrawler
import os

class TestSentiment(unittest.TestCase):
    sentimentTester = Sentiment()

    def test_sentimentNegative(self) :
        testingSentence = """ตัดมาประยุทธ ให้ท้องที่อายัดทรัพย์ให้ได้ปีละ 5,000 ล้านอิห่าส่วยแบบ ไทยแลนด์ 4.0"""
        predictedResult = "neg"
        result = self.sentimentTester.sentiment(testingSentence)
        self.assertEqual(result, predictedResult)

    def test_sentimentPositive(self) :
        testingSentence = """หนังนี้ก็สนุก"""
        predictedResult = "pos"
        result = self.sentimentTester.sentiment(testingSentence)
        self.assertEqual(result, predictedResult)

    def test_sentimentNegation(self) :
        testingSentence = """หนังเรื่องนี้ไม่ดีเลย"""
        predictedResult = "neg"
        result = self.sentimentTester.sentiment(testingSentence)
        self.assertEqual(result, predictedResult)

    def test_sentimentNeutral(self) :
        testingSentence = """จากการสำรวจพบว่า"""
        predictedResult = "neu"
        result = self.sentimentTester.sentiment(testingSentence)
        self.assertEqual(result, predictedResult)

    def test_sentimentNegative(self) :
        testingSentence = """The mouse will not fully charge. Also the mouse buttons have lateral movement making them overlap at times. This makes one mouse click actuate the other. Unacceptable at any price point let alone $150."""
        predictedResult = "neg"
        result = self.sentimentTester.sentiment(testingSentence)
        self.assertEqual(result, predictedResult)

    def test_sentimentPositive(self) :
        testingSentence = """And I say, Yes, I feel wonderful tonight."""
        predictedResult = "pos"
        result = self.sentimentTester.sentiment(testingSentence)
        self.assertEqual(result, predictedResult)



class TestTwitterCrawling(unittest.TestCase):
    trendyTester = Trendy()
    keyword ="โควิด"
    dateSince="2021-03-29"
    dateUntil="2021-03-31"


    def testInvalidDateCheck(self) :
        with self.assertRaises(Exception): self.trendyTester.isValidSinceUntil(since=self.dateUntil, until=self.dateSince)

    def testValidDateCheck(self) :
        self.assertEqual(True, self.trendyTester.isValidSinceUntil(since=self.dateSince, until=self.dateUntil))

    def testValidDateCheckNoneType(self) :
        self.assertEqual(True, self.trendyTester.isValidSinceUntil(since=None, until=None))

    def testDateCheck(self) :
        self.trendyTester.datecheck("โควิด","2021-03-30", self.dateUntil)
        cacheList = os.listdir("{}/data/twitterCrawler".format(os.getcwd()))
        print(cacheList)
        filename = "2021-03-30"+"_"+self.dateUntil+".csv"
        bool =  filename in cacheList
        self.assertEqual(True, bool)

    def testCombineCheck(self) :
        a = self.trendyTester.findAndCombineTrend("โควิด", self.dateSince, self.dateUntil)
        b = self.trendyTester.analyze("โควิด", self.dateSince, self.dateUntil)
        self.assertEqual(a,b)

    def testCombineCheckSentiment(self) :
        a = self.trendyTester.findAndCombineSentiment("โควิด", self.dateSince, self.dateUntil)
        b = self.trendyTester.sentimenTweet("โควิด", self.dateSince, self.dateUntil)
        self.assertEqual(a,b)

    def testCombineCheckLocation(self) :
        a = self.trendyTester.findAndCombineLocation("โควิด", self.dateSince, self.dateUntil)
        b = self.trendyTester.geopyToPandas("โควิด", self.dateSince, self.dateUntil)
        self.assertEqual(a.equals(b),True)

    def testAnalyze(self) :
        b = self.trendyTester.analyze("โควิด", self.dateSince, self.dateUntil)
        self.assertEqual(type(list()), type(b))

    def testSentimentTweet(self) :
        b = self.trendyTester.sentimenTweet("โควิด", self.dateSince, self.dateUntil)
        self.assertEqual(type(dict()), type(b))

    def testReadingData(self) :
        a = self.trendyTester.readingData(self.dateSince, self.dateUntil)
        self.assertEqual(a.empty, False)


class TestBiTools(unittest.TestCase) :

    stockTester = Buisy()
    validStockName = "DOGE"
    invalidStockName = "szDasd"
    dateSince = "2021-03-21"
    dateUntil = "2021-03-31"

    def testInvalidDateCheck(self) :
        with self.assertRaises(Exception): self.stockTester.getStock(self.validStockName, since=self.dateUntil, until=self.dateSince)

    def testInvalidName(self) :
        with self.assertRaises(Exception): self.stockTester.getStock(self.invalidStockName, since=self.dateSince, until=self.dateUntil)

    def testValidName(self) :
        self.assertEqual(type(tuple()), type(self.stockTester.getStock(self.validStockName, since=self.dateSince, until=self.dateUntil)))

    def testNone(self) :
        self.assertEqual(type(tuple()), type(self.stockTester.getStock(self.validStockName, since=None, until=None)))

class TestWebCrawling(unittest.TestCase) :

    webTester = WebCrawler()
    dateSince = "2021-04-27"
    dateUntil = "2021-04-29"

    def testReadingData(self) :
        a = self.webTester.readingData(self.dateSince, self.dateUntil)
        self.assertEqual(False, a.empty)

    def testSentimentTweet(self) :
        b = self.webTester.sentimenTweet("โควิด", self.dateSince, self.dateUntil)
        self.assertEqual(type(dict()), type(b))

    def testAnalyze(self) :
        b = self.webTester.analyze("โควิด", self.dateSince, self.dateUntil)
        self.assertEqual(type(list()), type(b))









if __name__ == "__main__" :
    unittest.main()
