#!/bin/bash
cd /code
source secrets.sh
clientid=${clientid//$'\r'} # remove escape character that may show up
token=${token//$'\r'}
python read.py /tmp/data.csv $clientid
influx write --bucket currently-airing-anime --file /tmp/data.csv \
    --header "#constant measurement,shows" \
    --header "#datatype tag,double,boolean,boolean,long,long,long,double,tag,long,long,long,long,boolean,boolean,dateTime:RFC3339" \
    --token $token
