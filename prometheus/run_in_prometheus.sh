#!/bin/bash

id=$(docker ps -f name=prometheus --format {{.ID}})
docker exec -it $id sh
