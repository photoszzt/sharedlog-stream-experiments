#!/bin/bash
  
while true; do 
    docker stats --format '{{json .}}' --no-stream | jq --arg timefield "$(date +%T)" '. + {time: $timefield}' >> $HOME/docker_stats.txt; 
    sleep 1; 
done
