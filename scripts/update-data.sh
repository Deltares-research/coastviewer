#!/bin/bash

# Download data
if [[ -d /data ]]
then
    cd /data
    make -f /app/data/Makefile clean
    make -f /app/data/Makefile
    cd -
else
    cd data
    make clean
    make
    cd -
fi
