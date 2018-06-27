#!/bin/bash

# Create data
if [[ ! -f /data/transect.nc ]] && [[ ! -f data/transect.nc ]]
then
    echo "data not found, creating dataset"
    if [[ -d /data ]]
    then
        cd /data
        make -f /app/data/Makefile
        cd -
    else
        cd data
        make
        cd -
    fi
else
    echo "data exists, let's get to work"
fi

# start the server
coastviewer
