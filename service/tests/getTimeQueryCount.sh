#!/bin/bash

curl -XPOST -H 'Content-Type: application/json' http://localhost:9200/default_index/_count?pretty -d \
'{
  "query":{
    "range":{
      "@timestamp":{
        "gt": "now-2d"
      }
    }
   }
}'

