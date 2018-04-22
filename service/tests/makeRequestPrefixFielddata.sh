#!/bin/bash

# Note the '_mapping/doc'. That is the mapping created by default. We are just modifying it
#curl -H 'Content-Type: application/json' -XPUT http://localhost:9200/default_index/_mapping/doc?update_all_types -d \ 
curl -H 'Content-Type: application/json' -XPUT http://localhost:9200/default_index/_mapping/doc -d \
'{
  "properties":{
     "requestPrefix" : {
            "type" : "text",
            "fields" : {
              "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
              }
            },
            "fielddata" : true
          }
  }
}'
