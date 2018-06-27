# Coastviewer
Coast viewer server side. Serves several sources as KML and geojson.

Read the documentation at http://coastviewer.readthedocs.io/

# Download data
For linux/ubuntu systems:
``` shell
cd data
make
```
For windows systems:
Install chocolatey from https://chocolatey.org/install
``` shell
choco install make
choco install wget
cd data
make
```

# Install dependencies (docker)
Install docker (for windows 7 or lower install docker terminal) from https://docs.docker.com/engine/installation/.

``` shell
docker pull openearth/coastviewer
```

# Install dependencies (development)

Install dependencies
On linux/ubuntu systems:
- apt-get install GDAL
- apt-get install python35

On windows systems:
Install GDAL, see tutorial from https://sandbox.idre.ucla.edu/sandbox/tutorials/installing-gdal-for-windows/.

Install python 3.5 from https://www.python.org/downloads/release/python-350/.

``` shell
pip install -e .
```
Install the requirements:

``` shell
pip install -r requirements.txt
```


# Run the server (docker)

``` shell
docker run openearth/coastviewer
# you can mount your local directory and expose the port like this
docker run -p5000:5000 --mount type=bind,source="$(pwd)"/data,target=/app/data
# To update the data you can run the update-data.sh under scripts
docker run scripts/update-data.sh
# For running in Amazon you can set the EFS environment variable to your data efs
docker run -e EFS=.... scripts/udpate-data.sh
```

# Run the server (development)

``` shell
coastviewer
```


# Use
Load the link [http://localhost:5000/coastviewer/1.1.0/transects/kml](transects/kml) in Google Earth (add network link).

# Test
Load the [http://localhost:5000/coastviewer/1.1.0/ui](test ui) in your browser. for the integration tests.
Run `make test` for the unit tests.
Run `make lint` for code formatting checks.
