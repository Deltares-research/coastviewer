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

# authenticate if needed
if [[ ! -z "${GEE_AUTHORIZATION_CODE}" ]]
then
    echo "autenticating earthengine"
    earthengine authenticate --quiet --authorization-code ${GEE_AUTHORIZATION_CODE}
else
    echo "not authenticating, no GEE_AUTHORIZATION_CODE set"
    env
fi

# start the server
coastviewer
