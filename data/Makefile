all: transect.nc BKL_TKL_TND.nc DF.nc MKL.nc strandbreedte.nc MHW_MLW.nc nourishments.nc faalkans.nc faalkans_PC-Ring.nc

clean:
	rm -f *.nc
# local copy of netcdf file, for performance reasons
transect.nc:
	wget -q -c http://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/jarkus/profiles/transect.nc

BKL_TKL_TND.nc:
	wget -q -c http://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/BKL_TKL_MKL/BKL_TKL_TND.nc

DF.nc:
	wget -q -c 'http://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/DuneFoot/DF.nc'

MKL.nc:
	wget -q -c 'http://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/BKL_TKL_MKL/MKL.nc'

strandbreedte.nc:
	wget -q -c 'http://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/strandbreedte/strandbreedte.nc'

MHW_MLW.nc:
	wget -q -c 'http://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/MHW_MLW/MHW_MLW.nc'

nourishments.nc:
	wget -q -c 'http://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/suppleties/nourishments.nc'

faalkans.nc:
	wget -q -c 'http://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/faalkans/faalkans.nc'

faalkans_PC-Ring.nc:
	wget -q -c 'http://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/faalkans/faalkans_PC-Ring.nc'
