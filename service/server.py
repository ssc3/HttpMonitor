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


class AlertMsg():
    '''
    A class which represents the object to be printed for alerts
    '''

    def __init__(self, aInTimeStamp, aInMsg, aInCount):
        self.timeStamp = aInTimeStamp
        self.msg = aInMsg
        self.count = aInCount

prevAlertsHistory = []

class TableData():
    '''
    A class which represents the object to be printed for HITs summary
    '''
    def __init__(self, aInSection, aInCount):
        self.section = "/" + aInSection
        self.count = aInCount
        self.timedCount = 0

    def getSectionAndCount(self):
        return self.section, self.count, self.timedCount

    def setTimed(self, aInTimedCount):
        self.timedCount = aInTimedCount

def printTable(aInList=None):
    '''
    Print summary of hits in an asciiart console table
    '''
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
    checkAndDisplayAlert(nowTime)


def endEventSection(aInScheduler, aInStartTime, aInEventName):
    print("----------------- EVENT DONE -----------------------")
    print("----------------------------------------------------\n\n")


def printAllAlertMsgs():
    print('\n')
    
    print("Historical Alerts")
    
    for item in reversed(prevAlertsHistory):
        if item.count != 0:
            print(str(item.timeStamp) + " seconds: " + item.msg)

    print('\n')
    

def checkAndDisplayAlert(aInTimeStamp):
    '''
    Queries datastore to get count of newly found logs in last 2 mins.
    Prints any new threshold crossing message and all historical alert messages
    '''
    count = esquery.getHitCountLastMins("2m")
    threshold = 30000
    if (count > threshold):
        alertMsg = "***NEW NEW NEW: ALERT***: Threshold crossed in last 2 mins. Threshold={}, Hits={}".format(threshold, count) 
        newAlertItem = AlertMsg(aInTimeStamp, alertMsg, count)
        lastItem = prevAlertsHistory[-1]
        if lastItem.count != newAlertItem.count:
            prevAlertsHistory.append(newAlertItem)
            print(alertMsg)
    else:
        print("No new Alerts")
    
    printAllAlertMsgs()

def displayTopHits(aInScheduler, aInStartTime, aInEventName, aInPeriod, aInPriority):
    '''
    An event which is called every 10s to display top hits and to check for alerts
    Uses key value map to record all time top HITs and then, gets HITs on those urls for the last 10s
    Then it sorts that map in a lambda function before printing it.

    The sorting and printing should really be a separate thread
    '''
    startEventSection(aInScheduler, aInStartTime, aInEventName)
 
    top10, top10timed = esquery.getTopHits(10)
    tableDataList = []

    resultObjMap = {}
    for item in top10:
        newData = TableData(item["key"], item["doc_count"])
        resultObjMap[item["key"]] = newData

    for item in top10timed:
        try:  
            curObj = resultObjMap.get(item["key"])
            curObj.setTimed(item["doc_count"])
        except:
            pass

    for k, v in resultObjMap.items():
        tableDataList.append(v)

    tableDataList.sort(key=lambda x: x.count, reverse=True)
        
    printTable(tableDataList)

    ipBuckets = esquery.getTopIpLastMins()
    print("--Additional Info--")
    topIp = ""
    try:
        topIp = ipBuckets[0]["key"]
    except:
        topIp = ""

    print("TOP client IP last 10s: " + str(topIp))
    
    aInScheduler.enter(aInPeriod, aInPriority, displayTopHits, (aInScheduler, aInStartTime, aInEventName, aInPeriod, aInPriority))
    endEventSection(aInScheduler, aInStartTime, aInEventName)

def begin():
    try:
        docCount = esquery.init()
        
    except Exception:
        print ("Could not initialize esquery. Restart docker")
        print(traceback.format_exc())
        sys.exit(1)

    sentinelAlert = AlertMsg(0.0, "", 0)
    prevAlertsHistory.append(sentinelAlert)

    print ("ElasticSearch started with " + str(docCount) + " docs")

    scheduler = sched.scheduler(time.time, time.sleep)
    startTime = time.time()

    print("EVENT: {} name={} elapsed={} secs".format(time.ctime(startTime), "START", 0))

    scheduler.enter(10, 1, displayTopHits, (scheduler, startTime, "displayTopHits", 10, 1))
    scheduler.run()

if __name__=="__main__":
    print("Starting HTTP Monitor")
    begin()
