#!/bin/bash


curl -H 'Content-Type: application/json' -XPOST http://localhost:9200/default_index/_search?pretty -d \
'{
  "size": 0,
  "aggs":{
    "req_count": {
      "terms":{
        "field": "clientip",
        "order": {"_count": "desc"}
       }
    }
  }
}'
