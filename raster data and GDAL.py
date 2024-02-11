import os
from osgeo import gdal
import numpy as np

# 1. Identify the overlap area between the different raster files (i.e., the maximum common extent).
# Once you have found this area, store the respective coordinates of all four corners as variables.
path = "/Users/tolgasabanoglu/Desktop/geoinpython/Assignment02_data/"
os.chdir(path)

tif_files = ["tileID_410_y2000.tif", "tileID_410_y2005.tif", "tileID_410_y2010.tif", "tileID_410_y2015.tif", "tileID_410_y2018.tif"]

min_x = None
max_x = None
min_y = None
max_y = None

for tif_file in tif_files:
    dataset = gdal.Open(tif_file)

    extent = dataset.GetGeoTransform()

    if min_x is None or extent[0] > min_x:
        min_x = extent[0]
    if max_x is None or extent[0] + extent[1] * dataset.RasterXSize < max_x:
        max_x = extent[0] + extent[1] * dataset.RasterXSize
    if min_y is None or extent[3] + extent[5] * dataset.RasterYSize > min_y:
        min_y = extent[3] + extent[5] * dataset.RasterYSize
    if max_y is None or extent[3] < max_y:
        max_y = extent[3]

# print the coordinates of all four corners of the valid extent
print("Common Extent Coordinates:")
print(f"Top-Left: ({round(min_x, 3)}, {round(max_y, 3)})")
print(f"Top-Right: ({round(max_x, 3)}, {round(max_y, 3)})")
print(f"Bottom-Left: ({round(min_x, 3)}, {round(min_y, 3)})")
print(f"Bottom-Right: ({round(max_x, 3)}, {round(min_y, 3)})")

# 2. Write a function that reads a specified geographic subset of an image and returns the subset as an array.
def read_geographic_subset(tif_file, min_x, max_x, min_y, max_y):
    try:
        dataset = gdal.Open(tif_file)
        if dataset is not None:
            transform = dataset.GetGeoTransform()
            px_min = int((min_x - transform[0]) / transform[1])
            px_max = int((max_x - transform[0]) / transform[1])
            ln_min = int((max_y - transform[3]) / transform[5])
            ln_max = int((min_y - transform[3]) / transform[5])
            subset_array = dataset.ReadAsArray(px_min, ln_min, px_max - px_min, ln_max - ln_min)
            dataset = None
            return subset_array
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# 3. Apply your function to read the subset area identified in (1) for each image.
# Calculate for each subset array the mean and store the values as variables.
means = []
for tif_file in tif_files:
    subset = read_geographic_subset(tif_file, min_x, max_x, min_y, max_y)
    if subset is not None:
        subset_mean = np.mean(subset)
        means.append(subset_mean)
        print(f"Mean for {tif_file}: {subset_mean}")
    else:
        print(f"Unable to calculate mean for {tif_file}. Subset is out of range.")

# store the mean values as variables
mean_2000, mean_2005, mean_2010, mean_2015, mean_2018 = means
