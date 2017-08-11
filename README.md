# Coastviewer
Coast viewer server side. Serves several sources as KML and geojson.

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
