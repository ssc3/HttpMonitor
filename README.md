# elk-docker# HttpMonitor

# REQUIREMENTS:
* docker
* docker-compose version 3
* python3

# HOW TO RUN?
* cd HttpMonitor
* ./run_docker_compose.sh

In another tab do:
* python3 service/server.py

To generate traffic, in another tab do:
* ./generate_logs.sh


# DESIGN CONSIDERATIONS:

The general architecture is:

On ingestion side:
* -> generate access.log
* -> logstash ingests and puts into elasticsearch 
* -> elasticsearch indexes it

On display side:
* -> HttpMonitor runs stateless
* -> Event generated every 10s
* -> Event checks for running average hits last 2 mins
* -> In the same event query top hits overall, top hits last 10s, top client IP last 10s. A few of these queries are combined
* -> PrettyPrint in a table



The general workfow is:
* 1. Docker starts elasticsearch and logstash

* 2. Input to logstash is an access.log file and output is elastisearch (see: logstash/conf/pipeline.conf)

Logstash is configured to create a new field in documents dumped into elastic search.
This feild is called "section". The reason for doing this to create an index on "section" for faster queries.
An alternative slow but intuitive way to do this would be to just dump docs and for every query, just parse all documents and 
create a map in memory with key = section and value = count of how many times that section got hit.

This consumes heap memory but gives higher speed. Tradeoff. For a real time app maybe put this system on a machine with much more memory available.

* 3. Logstash ingests access.log as soon as it gets generated and elasticsearch stores and indexes them

* 4. Any query can now be served rapidly from elasticsearch. Example queries used to get top hits and others are in service/esquery.py

* 5. Special attention is taken to make sure we make fewer network calls to the db server. This is to reduce network traffic and do most work in memory in local server



# WHAT THINGS WERE NOT DONE?
* 1. Better coding architecture. Typically, we would have a esquery class with private querying functions and limited public functions. Right now, I have them all as not part of a class. Why? Because I don't have time to do all this without know what it counts for

* 2. There is a latency between log generation and elasticsearch making that data available for querying (probably a gap of seconds). This needs more time to investigate

* 3. I dould have calculated running average in memory for alerting about traffic in past 2 mins. I chose not to do it and just wet ahead with querying elasticsearch. Why? Because running average calculation will take more time and I'm not sure I get credit for putting in that effort in a takehome

* 4. I did not use logging. Everything is printed

* 5. No persistent storage to accompany elasticsearch. I considered cassandra before elasticsearch but decided against it since without info, I assumed that the application speed was more important than long term storage. If long term persisten storage is necessary, it should have been mentioned

* 6. No thought to scaling and redundancy/availability since no credit for it

* 7. Python could have used threading for events but I decided against it to focus on actual output

* 8. No batching of queries. With the small description, it didn't seem like batching is necessary

