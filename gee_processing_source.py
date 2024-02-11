import ee
import geemap
import pandas as pd

# Initialize Earth Engine
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# Load FAO GAUL dataset
roiSHP = ee.FeatureCollection("FAO/GAUL/2015/level0")

# Filter to get Germany geometry
roiLYR = roiSHP.filter(ee.Filter.eq('ADM0_NAME', 'Germany'))

# Get the first feature from the filtered collection
roiFEAT = roiLYR.first()

# Get the geometry of the first feature
roiGEOM = roiFEAT.geometry()

# Sample random points across Germany
numPoints = 5000  # Adjust this number as needed

# Create an empty list to store feature collections
featCollections = []

# Define the number of points to generate in each batch
batchSize = 10000

# Generate random points in batches
for batchStart in tqdm(range(0, numPoints, batchSize)):
    batchEnd = min(batchStart + batchSize, numPoints)
    batchPoints = ee.FeatureCollection.randomPoints(roiGEOM, batchEnd - batchStart)
    featCollections.append(batchPoints)

# Merge the feature collections
ptsSHP = ee.FeatureCollection(featCollections).flatten()

# Convert the Earth Engine geometry to a JSON-like format
geomJSON = roiGEOM.getInfo()

# Extract the coordinates for a LineString
geomCOORD = geomJSON['geometries'][0]['coordinates']

# Create an Earth Engine geometry from the coordinates
geomEE = ee.Geometry.LineString(coords=geomCOORD)

# Create an empty list that we populate
featList = []

# Iterate over all features in `ptsSHP`
for idx, feat in tqdm(enumerate(ptsSHP.getInfo()['features'])):
    # Use the feature index as a makeshift ID
    pid = idx
    
    gcoord = feat['geometry']['coordinates']
    gEE = ee.Geometry.Point(coords=gcoord)
    # Create ee.Feature(), append to list
    eeFeat = ee.Feature(gEE, {"UniqueID": pid})
    featList.append(eeFeat)

# Convert the list into ee.FeatureCollection()
fc = ee.FeatureCollection(ee.List(featList))

# Prepare STMs
def ScaleMask_l89(img):
    # Scale the bands
    refl = img.select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']).multiply(0.0000275).add(-0.2)
    img_SR = ee.Image(refl).addBands(img.select(['QA_PIXEL']))
    # Mask cloud
    qa = ee.Image(img_SR).select(['QA_PIXEL'])
    dilatedCloud = qa.bitwiseAnd(1 << 1)
    cirrusMask = qa.bitwiseAnd(1 << 2)
    cloud = qa.bitwiseAnd(1 << 3)
    cloudShadow = qa.bitwiseAnd(1 << 4)
    snow = qa.bitwiseAnd(1 << 5)
    water = qa.bitwiseAnd(1 << 7)
    clear = dilatedCloud.Or(cloud).Or(cloudShadow).eq(0)
    cfmask = (clear.eq(0).where(water.gt(0), 1)
              .where(snow.gt(0), 3)
              .where(dilatedCloud.Or(cloud).gt(0), 4)
              .where(cloudShadow.gt(0), 2)
              .rename('cfmask'))
    img_SR_cl = ee.Image(img_SR).select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']).mask(cfmask.lte(2))
    return img_SR_cl

# Get the collections, merge them
l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
    .filterDate('2023-03-01', '2023-11-30').filter(ee.Filter.lt('CLOUD_COVER', 70)).filterBounds(geomEE)
l9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
    .filterDate('2022-03-01', '2023-11-30').filter(ee.Filter.lt('CLOUD_COVER', 70)).filterBounds(geomEE)
lAll = l8.merge(l9)

# Apply masking and filtering
lALL_masked = lAll.map(ScaleMask_l89)

# Define reducers
mean = ee.Reducer.mean().unweighted()
sd = ee.Reducer.stdDev().unweighted()
percentiles = ee.Reducer.percentile([10, 25, 50, 75, 90]).unweighted()
allMetrics = mean.combine(sd, sharedInputs=True).combine(percentiles, sharedInputs=True)

# Apply reducers
stm = lALL_masked.reduce(allMetrics)

# Extract values at the point locations
vals = stm.sampleRegions(collection=fc, properties=['UniqueID'], scale=30, tileScale=4, geometries=False).getInfo()
flag = 0
featureValues = vals['features']
for f in featureValues:
    prop = f['properties']
    if flag == 0:
        out_pd = pd.DataFrame(prop, index=[0])
        flag = 1
    else:
        out_pd = pd.concat([out_pd, pd.DataFrame(prop, index=[0])])

# Parameterization in scikit-learn and conversion into GEE-classifier
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from geemap import ml

# Create the two arrays
y = out_pd['2021_Map']
X = out_pd.drop(['2021_Map', 'UniqueID'], axis=1)

# Create a classifier instance
RF = RandomForestClassifier(random_state=1)
param_grid = {'n_estimators': [10, 25, 50, 75, 100],
              'max_features': [5, 10, 'sqrt'],
              'min_samples_split': [5, 10, 15],
              'max_depth': [5, 10, 20]}
RF_cv = GridSearchCV(RF, param_grid=param_grid, cv=3, refit=True, n_jobs=4).fit(X, y)
best_mod = RF_cv.best_estimator_
feature_names = X.columns.tolist()  # get the names of the variables
best_mod_str = ml.rf_to_strings(best_mod, feature_names)
ee_classifier = ml.strings_to_classifier(best_mod_str)

# classification
classification = stm.classify(ee_classifier)

task = ee.batch.Export.image.toDrive(
    image=classification,
    description='Germany_Class_Export',
    folder='Week10_prediction',
    fileNamePrefix='Germany_Class_Export',
    region=geomEE,
    scale=30)

task.start()
