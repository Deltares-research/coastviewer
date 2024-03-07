FROM mambaorg/micromamba:1.4.4
MAINTAINER Fedor Baart <fedor.baart@deltares.nl>
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

USER root
RUN \
    apt-get update --fix-missing && \
    apt-get install -y apt-utils && \
    # echo "deb http://httpredir.debian.org/debian jessie-backports main non-free" >> /etc/apt/sources.list && \
    # echo "deb-src http://httpredir.debian.org/debian jessie-backports main non-free" >> /etc/apt/sources.list && \
    apt-get install -y wget unzip build-essential jq sudo tini dos2unix git && \
    apt-get clean

USER $MAMBA_USER

COPY --chown=$MAMBA_USER:$MAMBA_USER env.yaml /tmp/env.yaml
RUN micromamba install --yes --file /tmp/env.yaml && \
    micromamba clean --all --yes

# Make sure that mamba will be activated from here on.
# (otherwise python will not be found)
# see _dockerfile_shell.sh in mamba dockerfile
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# update system and install wget

# copy the app
COPY ./ /app/
# disable rendering to screen
ENV MPLBACKEND Agg
# dependencies and ap
WORKDIR /app

# Data directory
VOLUME /data
# this is our public port
EXPOSE 5000
# not sure what this is
ENTRYPOINT [ "/usr/bin/tini", "--" ]
# Fill the /data directory and let's get to wrk
# uncomment this line when building the docker on Windows
# RUN dos2unix /app/scripts/run.sh
CMD [ "/app/scripts/run.sh" ]
