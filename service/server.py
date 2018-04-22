#!/usr/bin/env python3

import logging
import sched
import time
import esquery
import traceback
from prettytable import PrettyTable


tab = PrettyTable()
headings = ['Section', 'Visit count']
tab.field_names = headings

class TableData():

    def __init__(self, aInSection, aInCount):
        self.section = "/" + aInSection
        self.count = aInCount

    def getSectionAndCount(self):
        return self.section, self.count


def printTable(aInList=None):

    tab.clear_rows()

    for item in aInList:
        section, count = item.getSectionAndCount()
        row = []
        row.append(section)
        row.append(count)
        tab.add_row(row)
 
    print (tab)

def startEventSection(aInScheduler, aInStartTime, aInEventName):
    nowTime = time.time()
    elapsed = int(nowTime-aInStartTime)
    print("EVENT: {} name={} elapsed={} secs".format(time.ctime(nowTime), aInEventName, elapsed))


def endEventSection(aInScheduler, aInStartTime, aInEventName):
    print("----------------- EVENT DONE -----------------------")



def displayTopHits(aInScheduler, aInStartTime, aInEventName, aInPeriod, aInPriority):
    startEventSection(aInScheduler, aInStartTime, aInEventName)

    top10 = esquery.getTopHits(10)
    tableDataList = []
    for item in top10:
        newData = TableData(item["key"], item["doc_count"])
        tableDataList.append(newData)
        
    printTable(tableDataList)


    aInScheduler.enter(aInPeriod, aInPriority, displayTopHits, (aInScheduler, aInStartTime, aInEventName, aInPeriod, aInPriority))
    endEventSection(aInScheduler, aInStartTime, aInEventName)



def alertTrafficThreshold(aInScheduler, aInStartTime, aInEventName, aInPeriod, aInPriority):
    startEventSection(aInScheduler, aInStartTime, aInEventName)
    
    count = esquery.getHitCountLastMins("2d")
    threshold = 5
    if (count > threshold):
        print("***ALERT ALERT ALERT ***: Threshold crossed in last 2 seconds. Threshold={}, Hits={}".format(threshold, count))

    aInScheduler.enter(aInPeriod, aInPriority, alertTrafficThreshold, (aInScheduler, aInStartTime, aInEventName, aInPeriod, aInPriority))
    endEventSection(aInScheduler, aInStartTime, aInEventName)

def begin():
    try:
        docCount = esquery.init()
        print ("ElasticSearch started with " + str(docCount) + " docs")
    except Exception:
        print ("Could not initialize esquery")
        print(traceback.format_exc())

    scheduler = sched.scheduler(time.time, time.sleep)
    startTime = time.time()
    print("EVENT: {} name={} elapsed={} secs".format(time.ctime(startTime), "START", 0))
    scheduler.enter(5, 1, displayTopHits, (scheduler, startTime, "displayTopHits", 5, 1))
    scheduler.enter(10, 2, alertTrafficThreshold, (scheduler, startTime, "Traffic ALERT", 10, 2))

    scheduler.run()


if __name__=="__main__":
    logging.info("Starting HTTP Monitor")
    begin()
