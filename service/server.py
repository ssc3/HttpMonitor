#!/usr/bin/env python3

import logging
import sched
import time
import esquery
import traceback
import sys
from prettytable import PrettyTable


tab = PrettyTable()
headings = ['Section', 'Total HITs', 'HITs last 10s']
tab.field_names = headings

class TableData():

    def __init__(self, aInSection, aInCount):
        self.section = "/" + aInSection
        self.count = aInCount
        self.timedCount = 0

    def getSectionAndCount(self):
        return self.section, self.count, self.timedCount

    def setTimed(self, aInTimedCount):
        self.timedCount = aInTimedCount


def printTable(aInList=None):

    tab.clear_rows()

    for item in aInList:
        section, count, timedCount = item.getSectionAndCount()
        row = []
        row.append(section)
        row.append(count)
        row.append(timedCount)
        tab.add_row(row)
 
    print (tab)

def startEventSection(aInScheduler, aInStartTime, aInEventName):
    nowTime = time.time()
    elapsed = int(nowTime-aInStartTime)
    print("NEW EVENT: {} name={} elapsed={} secs".format(time.ctime(nowTime), aInEventName, elapsed))


def endEventSection(aInScheduler, aInStartTime, aInEventName):
    print("----------------- EVENT DONE -----------------------")



def displayTopHits(aInScheduler, aInStartTime, aInEventName, aInPeriod, aInPriority):
    startEventSection(aInScheduler, aInStartTime, aInEventName)

    top10, top10timed = esquery.getTopHits(10)
    tableDataList = []

    resultObjMap = {}
    for item in top10:
        newData = TableData(item["key"], item["doc_count"])
        resultObjMap[item["key"]] = newData

    for item in top10timed:
        curObj = resultObjMap.get(item["key"])
        curObj.setTimed(item["doc_count"])

    for k, v in resultObjMap.items():
        tableDataList.append(v)
        
    printTable(tableDataList)


    aInScheduler.enter(aInPeriod, aInPriority, displayTopHits, (aInScheduler, aInStartTime, aInEventName, aInPeriod, aInPriority))
    endEventSection(aInScheduler, aInStartTime, aInEventName)



def alertTrafficThreshold(aInScheduler, aInStartTime, aInEventName, aInPeriod, aInPriority):
    startEventSection(aInScheduler, aInStartTime, aInEventName)
    
    count = esquery.getHitCountLastMins("2m")
    threshold = 30000
    if (count > threshold):
        print("***ALERT ALERT ALERT ***: Threshold crossed in last 2 mins. Threshold={}, Hits={}".format(threshold, count))
    else:
        print("No Alerts")

    aInScheduler.enter(aInPeriod, aInPriority, alertTrafficThreshold, (aInScheduler, aInStartTime, aInEventName, aInPeriod, aInPriority))
    endEventSection(aInScheduler, aInStartTime, aInEventName)

def begin():
    try:
        docCount = esquery.init()
        
    except Exception:
        print ("Could not initialize esquery")
        print(traceback.format_exc())
        sys.exit(1)

    print ("ElasticSearch started with " + str(docCount) + " docs")
    scheduler = sched.scheduler(time.time, time.sleep)
    startTime = time.time()
    print("EVENT: {} name={} elapsed={} secs".format(time.ctime(startTime), "START", 0))
    scheduler.enter(10, 1, displayTopHits, (scheduler, startTime, "displayTopHits", 10, 1))
    scheduler.enter(120, 2, alertTrafficThreshold, (scheduler, startTime, "Traffic ALERT", 120, 2))
    
    scheduler.run()

    

if __name__=="__main__":
    logging.info("Starting HTTP Monitor")
    begin()
