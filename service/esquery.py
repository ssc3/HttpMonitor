#!/usr/bin/env python3

import requests
import logging
import json

#ES_SERVER_URL = "http://localhost:9200/default_index/_count?pretty"
ES_SERVER_URL = "http://localhost:9200"
ES_INDEX = "default_index"
ES_OPERATION = "_search"
ES_PRETTY = "pretty"


globalSession = requests.session()

def generateUrl(*args):
    url = "".join([*args])
    return url

def executeRequest(aInSession, aInMethod, aInHeaders, aInUrl, aInBody=None):
    if aInMethod.lower() == "get":
        logging.debug("Executing GET: " + aInUrl)
        res = aInSession.get(aInUrl, headers=aInHeaders)
    elif aInMethod.lower() == "post":
        logging.debug("Executing POST: " + aInUrl)
        res = aInSession.post(aInUrl, headers=aInHeaders, data=json.dumps(aInBody))
    elif aInMethod.lower() == "put":
        #logging.debug("Executing PUT: " + aInUrl)
        print("Executing PUT: " + aInUrl)
        res = aInSession.post(aInUrl, headers=aInHeaders, data=json.dumps(aInBody))

    return res
        

def prepareRestCallAndExecute(aInSession, aInMethod, aInUri, aInBody=None):
    headers = {"Content-Type": "application/json"}
    esUrl = generateUrl(ES_SERVER_URL, "/", ES_INDEX, "/", aInUri, "?", ES_PRETTY)
    return executeRequest(aInSession, aInMethod, headers, esUrl, aInBody) 
    
def checkEsServerStatus(aInSession):
    method = "GET"
    uri = "_count"
    res = prepareRestCallAndExecute(aInSession, method, uri)
    jRes = res.json()
    print (res.text)
    return jRes["count"]
    

def esCreateSectionFieldData(aInSession):
    method = "PUT"
    uri = "_mapping/doc"
    body = {
            "properties": {
                "section" : {
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
    print (res.text)
    return jRes["acknowledged"]

def esGetAggregate(aInSession):
    method = "POST"
    uri = "_search"
    body = {
               "size": 0,
               "aggs":{
                   "req_count": {
                       "terms":{
                           "field": "section"
                        }
                    }
                }
            }
    res = prepareRestCallAndExecute(aInSession, method, uri, body)
    jRes = res.json()
    print (res.text)
    return jRes["aggregations"]["req_count"]["buckets"]

    
     
def getTopHits(aInNum):
    buckets = esGetAggregate(globalSession)
    return buckets[:aInNum]
    
        
def init():
    esCreateSectionFieldData(globalSession)
    return checkEsServerStatus(globalSession)
    
