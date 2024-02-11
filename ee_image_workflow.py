# Import necessary libraries
import ee
import geemap.foliumap as geemap
import geopy_ee_workflows_fun as geopy

# Initialize Earth Engine
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# Landsat 8 surface reflectance data
l8sr = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")

# Geographic coordinate of a location (pin)
pin = ee.Geometry.Point([14.2, 53.3])

# Visualization parameters
cfmaskVis = {"opacity": 1, "bands": ["cfmask"], "palette": ["00ff08", "1043ff", "000000", "f8ff87", "f3fffa"]}
l8Vis = {"bands": ["SR_B4", "SR_B3", "SR_B2"], "min": 5000, "max": 20000}
l8rescaledVis = {"bands": ["SR_B4", "SR_B3", "SR_B2"], "min": 0, "max": 0.2}
l8stdVis = {"bands": ["SR_B5_stdDev", "SR_B4_stdDev", "SR_B3_stdDev"], "min": 0, "max": [0.13, 0.13, 0.13]}
ndviVis = {"palette": ['white', 'green'], "min": 0.2, "max": 1}

# Filter Landsat-8 images
filteredl8 = l8sr.filterDate('2018-03-15', '2018-09-15') \
                 .filter(ee.Filter.lt('CLOUD_COVER', 70)) \
                 .filterBounds(pin)

# Visualize the first image
firstImage = filteredl8.first()
Map = geemap.Map(center=[53.3, 14.2], zoom=8)
Map.addLayer(firstImage, l8Vis, "First Landsat Image")
Map

# Rescale and mask clouds from the first image
rescaled = geopy.l8rescale(firstImage)
masked = geopy.l8cloudmask(rescaled)

# Visualize rescaled and masked image
Map = geemap.Map(center=[53.3, 14.2], zoom=8)
Map.addLayer(rescaled, l8rescaledVis, "Rescaled first image")
Map.addLayer(masked, cfmaskVis, "Masked first image")
Map

# Cloudmask the Landsat 8 collection
filteredl8 = l8sr.filterDate('2018-03-15', '2018-09-15') \
                 .filter(ee.Filter.lt('CLOUD_COVER', 70)) \
                 .filterBounds(pin) \
                 .map(geopy.l8rescale) \
                 .map(geopy.l8cloudmask)

# Visualize the first image of the masked collection
firstImage = filteredl8.first()
Map.addLayer(firstImage, {"bands": ["SR_B4", "SR_B3", "SR_B2"]}, "Landsat Collection")
Map

# Calculate mean and median NDVI
l8ndvi = filteredl8.map(geopy.calcNdvi)
meanNdvi = l8ndvi.reduce(ee.Reducer.mean())
medianNdvi = l8ndvi.median()

Map.addLayer(meanNdvi, ndviVis, "NDVI mean")
Map.addLayer(medianNdvi, ndviVis, "NDVI median")
Map

# Spectral-temporal metrics
filteredl8_median = filteredl8.median()
filteredl8_std = filteredl8.reduce(ee.Reducer.stdDev())

Map.addLayer(filteredl8_median, l8rescaledVis, "Median - Landsat")
Map.addLayer(filteredl8_std, l8stdVis, "STD - Landsat")
Map

# Calculate image statistics for the median Landsat image
image_stats = geemap.image_stats(filteredl8_median, region=pin, scale=30)
print(image_stats.getInfo())

# Calculate median NDVI image for each month in 2022
def NdviMedian(month):
    m = ee.Number(month).int8()

    # Calculate start and end dates for the specified month
    startDate = ee.Date.fromYMD(2022, m, 1)
    endDate = startDate.advance(1, 'month').advance(-1, 'day')
    
    dateFilter = ee.Filter.And(
        ee.Filter.calendarRange(m, m, "month"),
        ee.Filter.date(startDate, endDate)
    )
    
    l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
             .filter(dateFilter) \
             .filter(ee.Filter.lt('CLOUD_COVER', 70)) \
             .filterBounds(pin) \
             .map(geopy.l8rescale) \
             .map(geopy.l8cloudmask) \
             .map(geopy.calcNdvi)
                      
    l9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
             .filter(dateFilter) \
             .filter(ee.Filter.lt('CLOUD_COVER', 70)) \
             .filterBounds(pin) \
             .map(geopy.l8rescale) \
             .map(geopy.l8cloudmask) \
             .map(geopy.calcNdvi)
    
    ndviMerge = l8.merge(l9)
    
    medianNdvi = ndviMerge.median()

    return medianNdvi.rename(ee.String("ndvi_").cat(m.format()))

# List including months
months = ee.List.sequence(1, 12)

# Create an ImageCollection of median NDVI images for each month
medianNdviAll = ee.ImageCollection(months.map(NdviMedian)).toBands()

# Visualize the median NDVI image for July
Map2 = geemap.Map(center=[53.3, 14.2], zoom=8)
Map2.addLayer(medianNdviAll.select(["7_ndvi_8"]), ndviVis, "Median NDVI - July")
Map2
