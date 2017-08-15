FROM continuumio/miniconda3
MAINTAINER Fedor Baart <fedor.baart@deltares.nl>
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
# update system and install wget
RUN \
    apt-get install -y apt-utils && \
    echo "deb http://httpredir.debian.org/debian jessie-backports main non-free" >> /etc/apt/sources.list && \
    echo "deb-src http://httpredir.debian.org/debian jessie-backports main non-free" >> /etc/apt/sources.list && \
    apt-get update --fix-missing && \
    apt-get install -y ffmpeg wget unzip build-essential
# switch to python 3.5 (no gdal in 3.6)
RUN conda create -y -n py35 python=3.5 libgdal gdal jpeg=8d netcdf4 matplotlib pandas pyproj
COPY ./ app/
RUN cd app/data && make
ENV PATH /opt/conda/envs/py35/bin:$PATH
ENV MPLBACKEND Agg
RUN cd app && pip install -r requirements.txt && pip install -e .
WORKDIR app
EXPOSE 5000
# not sure what this is
ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "coastviewer" ]
