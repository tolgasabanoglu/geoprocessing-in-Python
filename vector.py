import os
import numpy as np
from osgeo import ogr, osr, gdal

def CopySHPtoMem(path):
    drvMemV = ogr.GetDriverByName('Memory')
    f_open = drvMemV.CopyDataSource(ogr.Open(path),'')
    return f_open

def CopySHPDisk(shape, outpath):
    drvV = ogr.GetDriverByName('ESRI Shapefile')
    outSHP = drvV.CreateDataSource(outpath)
    lyr = shape.GetLayer()
    out = outSHP.CopyLayer(lyr, 'lyr')

# Lines to create a raster file (GTIFF)
rasterFile = gdal.GetDriverByName('GTIFF').Create('', #cols, rows, nbands, gdal.GDT_Float) #--> cols/rows/nbands are the properties of the raster to be created
rasterFile.SetGeoTransform() # Argument for the function is the prepared GeoTransform --> can be created individually or imported
rasterFile.SetProjection() # Same as above, but for the projection
# Line to rasterize a vector layer
# Example I: using a constant value of 1 for all polygons of the shapefile
gdal.RasterizeLayer(toRaster, [1], shp_lyr, burn_values=[1])

# Example II: using an attribute from the shapefile --> make sure you define the raster layer correctly
OPTIONS = ['ATTRIBUTE=' + field] # you can add more elements into the list
gdal.RasterizeLayer(toRaster, [1], shp_lyr, None, options=OPTIONS)

def calculate_housing_density(chaco_extent, grid_size, gpkg_path, raster_file):
    gpkg_ds = ogr.Open(gpkg_path)
    gpkg_layer = gpkg_ds.GetLayer()

    cols = int((chaco_extent[1] - chaco_extent[0]) / grid_size)
    rows = int((chaco_extent[3] - chaco_extent[2]) / grid_size)

    housing_density_array = np.zeros((rows, cols), dtype=np.float32)

    for row in range(rows):
        for col in range(cols):
            x_min = chaco_extent[0] + col * grid_size
            x_max = x_min + grid_size
            y_max = chaco_extent[3] - row * grid_size
            y_min = y_max - grid_size

            gpkg_layer.SetSpatialFilterRect(x_min, y_min, x_max, y_max)

            house_count = 0
            for feature in gpkg_layer:
                house_count += 1

            housing_density = house_count / 25.0

            housing_density_array[row, col] = housing_density

    raster_file.GetRasterBand(1).WriteArray(housing_density_array)

def main():
    chaco_path = "/Users/tolgasabanoglu/Desktop/geoinpython/vectordata/data/CHACO_outline_LAEA.shp"
    chaco_ds = ogr.Open(chaco_path)
    chaco_layer = chaco_ds.GetLayer()
    chaco_extent = chaco_layer.GetExtent()

    grid_size = 5000
    cols = int((chaco_extent[1] - chaco_extent[0]) / grid_size)
    rows = int((chaco_extent[3] - chaco_extent[2]) / grid_size)
    raster_file = gdal.GetDriverByName('GTIFF').Create('output.tif', cols, rows, 1, gdal.GDT_Float32)
    geo_transform = (chaco_extent[0], grid_size, 0, chaco_extent[3], 0, -grid_size)
    raster_file.SetGeoTransform(geo_transform)

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035)
    raster_file.SetProjection(srs.ExportToWkt())

    gpkg_files = [
        "/Users/tolgasabanoglu/Desktop/geoinpython/vectordata/data/tile93f.gpkg",
        "/Users/tolgasabanoglu/Desktop/geoinpython/vectordata/data/tile95d.gpkg",
        "/Users/tolgasabanoglu/Desktop/geoinpython/vectordata/data/tile939.gpkg",
        "/Users/tolgasabanoglu/Desktop/geoinpython/vectordata/data/tile941.gpkg",
        "/Users/tolgasabanoglu/Desktop/geoinpython/vectordata/data/tile943.gpkg",
        "/Users/tolgasabanoglu/Desktop/geoinpython/vectordata/data/tile945.gpkg",
        "/Users/tolgasabanoglu/Desktop/geoinpython/vectordata/data/tile947.gpkg",
        "/Users/tolgasabanoglu/Desktop/geoinpython/vectordata/data/tile969.gpkg"
    ]

    for gpkg_path in gpkg_files:
        calculate_housing_density(chaco_extent, grid_size, gpkg_path, raster_file)

    raster_file = None
