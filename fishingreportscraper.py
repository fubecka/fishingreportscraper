#!/root/fishreportscraper/venv/bin/python
from bs4 import BeautifulSoup
import urllib2
from pymongo import MongoClient
import pymongo
from datetime import datetime

client = MongoClient()
db = client['fishingscraper']
collection = db['reports']

def scrape_eddierobinsons():
    latest = collection.find({"source": "Eddie Robinson's Fly Fishing"}).sort('date',pymongo.ASCENDING).limit(1)
    url = 'http://www.eddierobinsons.com/reports/'
    r = urllib2.urlopen(url)
    soup = BeautifulSoup(r, 'html.parser')
    content = soup.find("div", {"class": "et_pb_text et_pb_bg_layout_light et_pb_text_align_left"})
    scrapelist = content.findAll("p")
    reportlist = []
    flow = ""

    for p in scrapelist:
        text = p.text
        if len(text.split()) > 20 and "CFS" in text:
            reportlist.append(text.split("Flows: ")[1].strip())
        elif len(text.split()) < 20 and "CFS" in text:
            flow = text.split("Flows: ")[1]
        elif len(text.split()) > 20 and "CFS" not in text:
            reportlist.append(flow + " " + text.strip())
    
    lower = reportlist[0]
    middle = reportlist[1]
    green = reportlist[2]
    
    result = {
        "source": "Eddie Robinson's Fly Fishing",
        "url": url,
        "date": datetime.utcnow(),
        "reports":[
            {"river": "Lower Provo River", "report": lower},
            {"river": "Middle Provo River", "report": middle},
            {"river": "Green River", "report": green},
            ]
        }
    
    try:
        for report in latest[0]['reports']:
            if report['river'] == "Lower Provo River":
                latestlower = report['report']
            elif report['river'] == "Middle Provo River":
                latestmiddle = report['report']
            elif report['river'] == "Green River":
                latestgreen = report['report']
        if latestlower != lower or latestmiddle != middle or latestgreen != green: 
            print latestlower
            print lower
            collection.insert(result)
        else:
            print "Still hasn't updated"
    except IndexError:
        collection.insert(result)     
        print "Shouldn't get here"

    
if __name__ == "__main__":
    scrape_eddierobinsons()
