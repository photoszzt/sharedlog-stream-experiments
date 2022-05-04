#!/bin/bash
curl localhost:8090/consume &
p1=$!
curl localhost:8080/produce &
p2=$!
wait ${p1}
wait ${p2}
