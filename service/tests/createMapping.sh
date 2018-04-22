#!/bin/bash

curl -H 'Content-Type: application/json' -XPUT http://localhost:9200/request_index?pretty -d \
'{
  "mappings":{
    "reqindex":{
      "properties":{
        "request": {"type": "text"}
       }
    }
}'

echo "REINDEXING NOW"


curl -H 'Content-Type: application/json' -XPOST http://localhost:9200/_reindex?pretty -d \
'{
  "source": {
    "index": "default_index"
  },
  "dest": {
    "index": "request_index"
  }
}'
