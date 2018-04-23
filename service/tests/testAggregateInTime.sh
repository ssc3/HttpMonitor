#!/bin/bash


curl -H 'Content-Type: application/json' -XPOST http://localhost:9200/default_index/_search?pretty -d \
'{
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
          { "from": "now/m-2d" }
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
}'

