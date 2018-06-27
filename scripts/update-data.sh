#!/bin/bash

# Mount EFS if set
if [ -n $EFS ]
then
    mkdir /tmp/efs
    mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=15,retrans=2 ${EFS}:/ /tmp/efs
    cd /tmp/efs
fi

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
