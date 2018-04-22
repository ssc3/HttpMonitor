#!/bin/bash

curl -XGET -H 'Content-Type: application/json' http://localhost:9200/default_index/_search?pretty -d \
'{
  "query":{
    "match":{
      "request": "css"
     }
  }
}'

