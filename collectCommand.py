from webCrawler  import WebCrawler
from twitterCrawler import Trendy
from datetime import date
import datetime

today = date.today()
nextday = today + datetime.timedelta(days=1)


app1 = Trendy()
trend = app1.viewTrends()
#app1.collectTrendData(trend, lang="th", quantity=50, mode='w') #collecting data in Twittter Trends
for k in trend :
    #app1.analyze(k, since=str(today), until=str(nextday), plot=False)
    pass


app = WebCrawler()
list =["https://apnews.com/",
        "https://news.google.com/topstories?hl=en-US&gl=US&ceid=US:en",
        "https://www.nationthailand.com/",
        "https://www.nbcnews.com/",
        "https://www.nytimes.com/",
        "https://abcnews.go.com/"
        "https://www.nbcnews.com/",
        "https://www.huffpost.com/",
        "https://www.nbcnews.com/",
        "https://www.cbsnews.com/",
        "https://www.usatoday.com/",
        "https://www.nytimes.com/",
        "https://www.foxnews.com/",
        "https://www.dailymail.co.uk/ushome/index.html/"
        "https://www.businessinsider.com/",
        "https://www.washingtonpost.com/",
        "https://elitedaily.com/",
        "https://www.cnet.com/",
        "https://www.cnbc.com/world/?region=world/",
        "https://www.marketwatch.com/",
        "https://www.investing.com/",
        "https://www.bangkokpost.com/",
        "https://www.cnet.com/",
        "https://www.theguardian.com/us/"
        "https://www.msn.com/en-us/news/",
        "https://www.npr.org/",
        "https://www.nydailynews.com/",
        "https://www.latimes.com/",
        "https://nypost.com/",
        "https://time.com/,",
        "https://mashable.com/",
        "https://www.sfgate.com/",
        "https://www.slate.com/",
        "https://www.upworthy.com/",
        "https://www.theblaze.com/",
        "https://www.telegraph.co.uk/",
        "https://www.usnews.com/",
        "https://www.vice.com/en_us/",
        "https://www.chron.com/",
        "https://gawker.com/",
        "https://www.vox.com/",
         "https://www.thedailybeast.com/",
        "https://www.salon.com/",
        "https://mic.com/",
        "https://www.mirror.co.uk/news/",
        "https://www.nj.com/",
        "https://www.independent.co.uk/",
        "https://www.freep.com/",
        "https://www.bostonglobe.com/",
        "https://www.theatlantic.com/",
        "https://www.mlive.com/",
        "https://www.engadget.com/",
        "https://techcrunch.com/",
        "https://www.boston.com/",
        "https://www.al.com/"]
listTH = ["https://www.sanook.com/news/",
          "https://www.thairath.co.th/news",
          "https://www.komchadluek.net/",
          "http://www.chiangmainews.co.th/",
          "http://www.matichon.co.th/",
          "http://www.dailynews.co.th/",
          "http://naewna.com/",
          "http://www.bangkokbiznews.com/",
          "http://www.khaosodusa.com/",
          "http://www.manager.co.th/",
          "http://www.thannews.th.com/",
          "http://www.siamturakij.com/",
          "http://www.bangkokpost.com/",
          "http://www.thaipost.net/",
          "http://www.nationmultimedia.com/",
          "http://www.komchadluek.com/",
          "http://www.sentang.com/",
          "http://www.siamsport.co.th/",
          "http://www.thaitv3.com/",
          "http://www.tv5.co.th/",
          "http://www.ch7.com/",
          "http://www.mcot.or.th/",
          "http://www.prd.go.th/",
          "http://www.itv.co.th/",
          "http://www.ubctv.com/",
          "http://www.nationchannel.com/",
          "http://www.samarts.com/",
          "http://www.thailand.com/"]
#app.analyzeEN("https://www.bangkokpost.com/",mode='w')



#collecting data all in list
for k in list :
    app.analyzeEN(k, mode='w',max_ring=2)
for k in listTH :
    app.analyzeTH(k, mode='w',max_ring=2)



#print(app.analyze_csv("", lang="th"))
#print(app.search("COVID-19"))
