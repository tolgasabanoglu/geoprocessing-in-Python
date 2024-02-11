# libraries
import geopandas as gpd
import rasterio
import numpy as np
import pandas as pd

# load gpkg
gpkg_path = '/Users/tolgasabanoglu/Desktop/geoinpython/datastm/berlin_lucas.gpkg'
gdf = gpd.read_file(gpkg_path)

# raster files
raster_files = [
    '/Users/tolgasabanoglu/Desktop/geoinpython/datastm/X0069_Y0043_landsat_stm_2018.tif',
    '/Users/tolgasabanoglu/Desktop/geoinpython/datastm/X0068_Y0043_landsat_stm_2018.tif',
    '/Users/tolgasabanoglu/Desktop/geoinpython/datastm/X0069_Y0044_landsat_stm_2018.tif',
    '/Users/tolgasabanoglu/Desktop/geoinpython/datastm/X0068_Y0044_landsat_stm_2018.tif'
]

# create lists to store data
point_ids = []
landcovers = []
raster_columns = {}

# iterate over each point in the GDF
for index, point in gdf.iterrows():
    # extract point ID and landcover
    point_id = point['point_id']
    landcover = point['landcover']
    
    # add point data to lists
    point_ids.append(point_id)
    landcovers.append(landcover)

    # iterate over raster files and extract values for each band
    for i, raster_file in enumerate(raster_files):
        # open raster file
        with rasterio.open(raster_file) as raster:
            # extract values at the point's location
            values = list(raster.sample([(point.geometry.x, point.geometry.y)]))
            
            # generate column names for each band
            for band, value in enumerate(values[0], start=1):
                col_name = f'raster_{i+1}_band_{band}'
                if col_name not in raster_columns:
                    raster_columns[col_name] = []
                raster_columns[col_name].append(value)

# create a DF from the lists
df = pd.DataFrame({
    'point_id': point_ids,
    'landcover': landcovers,
    **raster_columns
})

# save DF to a CSV file
output_csv = '/Users/tolgasabanoglu/Desktop/geoinpython/datastm/extracted.csv'
df.to_csv(output_csv, index=False)

# load extracted csv
df = '/Users/tolgasabanoglu/Desktop/geoinpython/datastm/extracted.csv'
df = pd.read_csv(df)

# print
print(df)
