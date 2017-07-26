# Coastviewer
Coast viewer server side. Serves several sources as KML and geojson.

# Download data

``` shell
cd data
make
```

# Install dependencies (docker)

``` shell
docker pull openearth/coastviewer
```

# Install dependencies (development)

Install dependencies

- apt-get install GDAL
- apt-get install python35

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
Load the [http://localhost:5000/coastviewer/1.1.0/ui](test ui) in your browser.
