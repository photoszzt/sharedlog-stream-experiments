#!/bin/bash
DIR=$1

cd "$DIR"
for i in $(ls .); do
    gzip -9 "$i"
done
