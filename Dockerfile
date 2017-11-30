FROM continuumio/miniconda3
MAINTAINER Fedor Baart <fedor.baart@deltares.nl>
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
# update system and install wget
RUN \
    apt-get install -y apt-utils && \
    echo "deb http://httpredir.debian.org/debian jessie-backports main non-free" >> /etc/apt/sources.list && \
    echo "deb-src http://httpredir.debian.org/debian jessie-backports main non-free" >> /etc/apt/sources.list && \
    apt-get update --fix-missing && \
    apt-get install -y wget unzip build-essential
RUN conda config --add channels conda-forge
RUN conda create -y -n py36 python=3.6 libgdal gdal netcdf4 matplotlib pandas pyproj
COPY ./ app/
ENV PATH /opt/conda/envs/py36/bin:$PATH
ENV MPLBACKEND Agg
RUN cd /app && pip install -r requirements.txt && pip install -e .
# Fill the /data directory
WORKDIR app
EXPOSE 5000
# not sure what this is
ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "scripts/run.sh" ]
