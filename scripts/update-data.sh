#!/bin/bash
echo "current directory: $(pwd)"

# Mount EFS if set
if [ -n $EFS ]
then
    mkdir /tmp/efs
    sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=15,retrans=2 ${EFS}:/ /tmp/efs
    cd /tmp/efs
fi

echo "current directory: $(pwd)"

# Download data
if [[ -d /data ]]
then
    cd /data
    echo "running Makefile"
    cat /app/data/Makefile
    make -f /app/data/Makefile clean
    make -f /app/data/Makefile
    cd -
else
    cd data
    echo "running Makefile"
    cat Makefile
    make clean
    make
    cd -
fi
