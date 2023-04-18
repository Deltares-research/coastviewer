FROM continuumio/miniconda3
MAINTAINER Fedor Baart <fedor.baart@deltares.nl>
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
# update system and install wget
RUN \
    apt-get update --fix-missing && \
    apt-get install -y apt-utils && \
    # echo "deb http://httpredir.debian.org/debian jessie-backports main non-free" >> /etc/apt/sources.list && \
    # echo "deb-src http://httpredir.debian.org/debian jessie-backports main non-free" >> /etc/apt/sources.list && \
    apt-get install -y wget unzip build-essential jq sudo tini dos2unix

RUN conda install mamba -n base -c conda-forge
# use anaconda to create an env

RUN mamba update -n base -c defaults conda
RUN mamba create -y -n py37 python=3.7 libgdal matplotlib gdal netcdf4 pyproj numpy pandas cffi scipy && \
    mamba clean --all --yes
# copy the app
COPY ./ app/
# manual activate env
ENV PATH /opt/conda/envs/py37/bin:$PATH
# disable rendering to screen
ENV MPLBACKEND Agg
# dependencies and ap
RUN cd /app && pip install -r requirements.txt && pip install -e .
WORKDIR /app

# Data directory
VOLUME /data
# this is our public port
EXPOSE 5000
# not sure what this is
ENTRYPOINT [ "/usr/bin/tini", "--" ]
# Fill the /data directory and let's get to wrk
RUN dos2unix /app/scripts/run.sh #uncomment this line when building the docker on Windows
CMD [ "/app/scripts/run.sh" ]
