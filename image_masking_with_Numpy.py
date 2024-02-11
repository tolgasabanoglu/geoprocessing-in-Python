import numpy as np
import os
from osgeo import gdal, gdal_array
from matplotlib import pyplot as plt
import geopy_array_manipulation_fun as geopy

gdal.UseExceptions()

# Clear observation mask
def mask_clouds(boa_file):
    # open BOA and QFM images
    boa_ds = gdal.Open(boa_file, gdal.GA_ReadOnly)
    qfm_file = boa_file.replace("BOA", "QFM")  
    qfm_ds = gdal.Open(qfm_file, gdal.GA_ReadOnly)

    # read BOA and QFM data as numpy arrays
    boa_data = gdal_array.DatasetReadAsArray(boa_ds).astype(np.float32)
    qfm_data = gdal_array.DatasetReadAsArray(qfm_ds)

    # create a mask for clear observations
    clear_mask = np.logical_or.reduce((qfm_data == 0, qfm_data == 1, qfm_data == 3))

    # apply the mask to the BOA image
    masked_boa = np.where(clear_mask, boa_data, np.nan)

    return masked_boa

# Demonstrate your mask function
# BOA image
boa_file = "20180808_LEVEL2_LND08_BOA.tif"

# apply the mask function 
masked_boa = mask_clouds(boa_file)

# visualize the masked BOA image 
geopy.plot_boa(masked_boa)

# Create a list of BOA images
# list all BOA file names in the directory
path = "/Users/tolgasabanoglu/Desktop/geoinpython/landsat8_berlin"
boa_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and 'BOA.tif' in f]

# print the list of BOA 
print(boa_files)

# Mean BOA image
def calculate_mean_boa(boa_files):
    sum_boa = None
    count = 0

    for boa_file in boa_files:
        boa_ds = gdal.Open(os.path.join(path, boa_file), gdal.GA_ReadOnly)

        # read the BOA data as a numpy array
        boa_data = gdal_array.DatasetReadAsArray(boa_ds).astype(np.float32)

        # sum of BOA images
        if sum_boa is None:
            sum_boa = np.zeros_like(boa_data)
        sum_boa += boa_data
        count += 1

    if count > 0:
        # calculate the mean by dividing the sum by the count
        mean_boa = sum_boa / count
        return mean_boa

# calculate the mean BOA image
mean_boa = calculate_mean_boa(boa_files)

# visualize the mean BOA image 
geopy.plot_boa(mean_boa)

# Save files to disk
# output dir
output_dir = "/Users/tolgasabanoglu/Desktop/geoinpython/landsat8_berlin"

# output file name 
output_file = os.path.join(output_dir, "mean_boa.tif")

# save the mean BOA image to disk
geopy.writeRaster(mean_boa, output_file, ref_file=os.path.join(path, boa_files[0]))

# Max NDVI Composite (optional)
# NDVI function
def calculate_ndvi(red_band, nir_band):
    # calculate NDVI
    ndvi = (nir_band - red_band) / (nir_band + red_band)
    return ndvi

# variables to store the maximum NDVI values and corresponding BOA reflectance
first_boa_ds = gdal.Open(os.path.join(path, boa_files[0]), gdal.GA_ReadOnly)
image_shape = (first_boa_ds.RasterYSize, first_boa_ds.RasterXSize, len(boa_files))
max_ndvi_boa = np.full(image_shape, -9999.0, dtype=np.float32)

# loop through the time series of BOA images
for i, boa_file in enumerate(boa_files):
    ds_src = gdal.Open(os.path.join(path, boa_file), gdal.GA_ReadOnly)
    nir_band = ds_src.GetRasterBand(4).ReadAsArray().astype(np.float32)
    ndvi = nir_band
    ndvi_mask = ndvi > max_ndvi_boa[:, :, i]
    max_ndvi_boa[ndvi_mask, i] = ndvi[ndvi_mask]

# output file name 
output_file = os.path.join(output_dir, "max_ndvi_composite.tif")

# save the maximum NDVI image 
geopy.writeRaster(max_ndvi_boa, output_file, ref_file=os.path.join(path, boa_files[0]))
