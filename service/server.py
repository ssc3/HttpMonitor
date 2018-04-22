#!/usr/bin/env python3

import logging
import sched
import time
import texttable as tt
import esquery
import traceback


tab = tt.Texttable()
headings = ['Section', 'Visit count']
tab.header(headings)


def printTable():
    sections = ['Sec11', 'Sec12', 'Sec13']

    vCount = ['100', '200', '300']

    for row in zip(sections, vCount):
        tab.add_row(row)
 
    res = tab.draw()
    print (res)


def displayTopHits(aInStartTime, aInEventName):
    nowTime = time.time()
    elapsed = int(nowTime-aInStartTime)
    printTable()
    print("EVENT: {} name={} elapsed={}".format(time.ctime(nowTime), aInEventName, elapsed))



def begin():
    print("In Begin")
    try:
        docCount = esquery.init()
        print ("ElasticSearch started with " + str(docCount) + " docs")
    except Exception:
        print ("Could not initialize esquery")
        print(traceback.format_exc())

    scheduler = sched.scheduler(time.time, time.sleep)

    startTime = time.time()
    print("START TIME = " + time.ctime(startTime))
    scheduler.enter(5, 1, displayTopHits, (startTime, "displayTopHits"))

    scheduler.run()


if __name__=="__main__":
    logging.info("Starting HTTP Monitor")
    begin()
