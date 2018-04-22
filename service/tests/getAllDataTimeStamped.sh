#!/bin/bash

curl -XPOST -H 'Content-Type: application/json' http://localhost:9200/default_index/_search?pretty -d \
'{
  "query":{
    "match_all": {}
   },
   "size": "1",
   "sort": [
     {
       "@timestamp": {  
         "order": "desc"
       }
     }
   ]
}'

