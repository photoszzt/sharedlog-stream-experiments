#!/bin/bash
DIR=$1

cd "$DIR"
for i in $(ls .); do
    gzip -f -9 "$i"
done
