#!/usr/bin/env python3

import requests
import logging
import json

# Format for Elasticsearch queries:
# ES_SERVER_URL = "http://localhost:9200/default_index/_count?pretty"
ES_SERVER_URL = "http://localhost:9200"
ES_INDEX = "default_index"
ES_OPERATION = "_search"
ES_PRETTY = "pretty"

DEBUG=0

globalSession = requests.session()

def generateUrl(*args):
    url = "".join([*args])
    return url

'''
Elasticsearch private functions. These are the functions to be used internally in this module
Ideally encapsulate these all in a class. Make below functions private
'''

def executeRequest(aInSession, aInMethod, aInHeaders, aInUrl, aInBody=None):
    if aInMethod.lower() == "get":
        logging.debug("Executing GET: " + aInUrl)
        res = aInSession.get(aInUrl, headers=aInHeaders)
    elif aInMethod.lower() == "post":
        logging.debug("Executing POST: " + aInUrl)
        res = aInSession.post(aInUrl, headers=aInHeaders, data=json.dumps(aInBody))
    elif aInMethod.lower() == "put":
        print("Executing PUT: " + aInUrl)
        res = aInSession.post(aInUrl, headers=aInHeaders, data=json.dumps(aInBody))

    return res
        

def prepareRestCallAndExecute(aInSession, aInMethod, aInUri, aInBody=None):
    headers = {"Content-Type": "application/json"}
    esUrl = generateUrl(ES_SERVER_URL, "/", ES_INDEX, "/", aInUri, "?", ES_PRETTY)
    return executeRequest(aInSession, aInMethod, headers, esUrl, aInBody) 
    
def checkEsServerStatus(aInSession):
    '''
    HELPER: Just executes a count to check if elastic search is running
    In real system, use health check calls
    '''
    method = "GET"
    uri = "_count"
    res = prepareRestCallAndExecute(aInSession, method, uri)
    jRes = res.json()
    if (DEBUG):
        print (res.text)
    return jRes["count"]
    

def esCreateSectionFieldData(aInSession):
    '''
    CREATE: Indexes section fielddata which is not indexed by default
    '''
    method = "PUT"
    uri = "_mapping/doc"
    body = {
               "properties":{
                   "section" : {
                       "type" : "text",
                       "fields" : {
                           "keyword" : {
                               "type" : "keyword",
                               "ignore_above" : 256
                           }
                       },
                       "fielddata" : True
                   },
                   "clientip" : {
                       "type" : "text",
                           "fields" : {
                               "keyword" : {
                               "type" : "keyword",
                               "ignore_above" : 256
                           }
                       },
                       "fielddata" : True
                   }
               }
           }  

    res = prepareRestCallAndExecute(aInSession, method, uri, body)
    jRes = res.json()
    if (DEBUG):
        print (res.text)
    return jRes["acknowledged"]

def esGetAggregate(aInSession, aInSecs=None):
    '''
    GET: Get all logs from last aInSecs and sort them by the custom index section
    '''
    method = "POST"
    uri = "_search"
    if aInSecs is None:
        aInSecs = '10s'
    body = {
               "size": 0,
               "aggs":{
                   "overall": {
                       "terms": {
                           "field": "section"
                       }
                   },
                   "by_time": {
                       "date_range": {
                           "field": "@timestamp",
                           "ranges": [
                               { "from": "now/s-" + aInSecs }
                           ]
                       },
                       "aggs": {
                           "top_count": {
                               "terms": {
                                   "field": "section"
                               }   
                           }
                       }
                   }
               }
           }


    res = prepareRestCallAndExecute(aInSession, method, uri, body)
    jRes = res.json()
    if (DEBUG):
        print (res.text)
    return jRes["aggregations"]["overall"]["buckets"], jRes["aggregations"]["by_time"]["buckets"][0]["top_count"]["buckets"]


def esGetAggregateIp(aInSession, aInSecs=None):
    '''
    GET: Get count of IPs in the last 10s in descending order
    '''
    method = "POST"
    uri = "_search"
    if aInSecs is None:
        aInSecs = '10s'
    body = {
               "size": 0,
               "aggs":{
                   "overall": {
                       "terms": {
                           "field": "clientip"
                       }
                   },
                   "by_time": {
                       "date_range": {
                           "field": "@timestamp",
                           "ranges": [
                               { "from": "now/s-" + str(aInSecs) }
                           ]
                       },
                       "aggs": {
                           "top_count": {
                               "terms": {
                                   "field": "clientip",
                                   "order": {"_count": "desc"}
                               }
                           }
                       }
                   }
               }
           }

    res = prepareRestCallAndExecute(aInSession, method, uri, body)
    jRes = res.json()
    if (DEBUG):
        print (res.text)
    return jRes["aggregations"]["by_time"]["buckets"][0]["top_count"]["buckets"]

def esGetHitCountLastMins(aInSession, aInMins=None):
    '''
    GET: Get a count of hits for last aInMins
    '''
    method = "POST"
    uri = "_count"
    if aInMins is None:
        aInMins = '2m'
    body = {
               "query":{
                   "range":{
                       "@timestamp":{
                           "gt": "now-"+aInMins
                       }
                   }
               }
           }
    res = prepareRestCallAndExecute(aInSession, method, uri, body)
    jRes = res.json()
    if (DEBUG):
        print (res.text)
    return jRes["count"]

'''
Exposed functions. These are the functions to be used by clients
Ideally encapsulate these all in a class. Make above functions private and below functions public
'''

def getTopHits(aInNum):
    buckets = esGetAggregate(globalSession)
    return buckets[:aInNum]

def getTopIpLastMins():
    buckets = esGetAggregateIp(globalSession)
    return buckets[:1]


def getHitCountLastMins(aInMins):
    count = esGetHitCountLastMins(globalSession, aInMins)
    return count
        
def init():
    esCreateSectionFieldData(globalSession)
    return checkEsServerStatus(globalSession)
    
