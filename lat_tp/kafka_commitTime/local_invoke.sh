#!/bin/bash
curl localhost:8090/run &
p1=$!
curl localhost:8080/produce &
p2=$!
wait ${p1}
wait ${p2}
