#!/bin/bash

curl -H 'Content-Type: application/json' -XPOST http://localhost:9200/_search?pretty -d '{"query":{"match": {"request": "style2.css"}}}'
