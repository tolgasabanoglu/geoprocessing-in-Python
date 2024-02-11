# Import necessary libraries
import os
import json
import geemap
import geopandas as gpd
import ee
from functools import partial

# Authenticate to Earth Engine
ee.Authenticate()
ee.Initialize()

# Helper function to convert a local layer feature to an ee.Feature
def local_to_ee_feature(feat):
    geom = feat.GetGeometryRef()
    geojson = json.loads(geom.ExportToJson())
    properties = {}
    for i in range(feat.GetFieldCount()):
        field_name = feat.GetFieldDefnRef(i).GetName()
        field_value = feat.GetField(i)
        properties[field_name] = field_value
    return ee.Feature(ee.Geometry(geojson), properties)

# Function to save drawn features as a .gpkg file
def save_drawn_features_as_gpkg(drawn_features, output_file):
    # Convert drawn features to ee.FeatureCollection
    features = ee.FeatureCollection(drawn_features)
    
    # Convert ee.FeatureCollection to GeoDataFrame
    gdf = geemap.ee_to_geopandas(features)
    
    # Save GeoDataFrame to a GeoPackage file
    gdf.to_file(output_file, driver='GPKG')

# Function to convert a local shapefile (.gpkg-file) to a feature collection
def shapefile_to_feature_collection(input_file):
    # Read the shapefile into a GeoDataFrame
    gdf = gpd.read_file(input_file)
    
    # Convert GeoDataFrame to ee.FeatureCollection
    features = geemap.geopandas_to_ee(gdf)
    
    return features

# Function to visualize datasets
def visualize_datasets(geometry):
    # Create an interactive map
    Map = geemap.Map()

    # Add the drawn features to the map
    Map.addLayer(geometry, {'color': '00FF00'}, 'Drawn Features')

    # Example Landsat, Sentinel-2, and MODIS datasets
    landsat_image = ee.Image('LANDSAT/LC08/C01/T1_TOA/LC08_044034_20200115')
    sentinel_image = ee.Image('COPERNICUS/S2/20151219T141523_20151219T142501_T35NMK')
    modis_image = ee.Image('MODIS/006/MOD13Q1/2019_01_01')

    # Clip images to the drawn features
    clipped_landsat = landsat_image.clip(geometry)
    clipped_sentinel = sentinel_image.clip(geometry)
    clipped_modis = modis_image.clip(geometry)

    # Visualization parameters for Landsat
    landsat_vis_params = {
        'bands': ['B4', 'B3', 'B2'],
        'min': 0,
        'max': 0.3,
        'gamma': 1.4
    }

    # Visualization parameters for Sentinel-2
    sentinel_vis_params = {
        'bands': ['B4', 'B3', 'B2'],
        'min': 0,
        'max': 0.3,
        'gamma': 1.4
    }

    # Visualization parameters for MODIS
    modis_vis_params = {
        'bands': ['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03'],
        'min': 0,
        'max': 3000
    }

    # Add the clipped images to the map
    Map.addLayer(clipped_landsat, landsat_vis_params, 'Clipped Landsat Image')
    Map.addLayer(clipped_sentinel, sentinel_vis_params, 'Clipped Sentinel-2 Image')
    Map.addLayer(clipped_modis, modis_vis_params, 'Clipped MODIS Image')

    # Display the map
    Map

# Use the drawing tools in the geemap functionality to create (and store) a geometry
def draw_geometry(file_path='drawn_geometry.gpkg', file_format='GPKG'):
    # Create an interactive map
    Map = geemap.Map()

    # Use the drawing tools to draw a geometry (rectangle in this case)
    drawn_geometry = Map.draw_last_feature()

    # Display the drawn geometry on the map
    Map.addLayer(drawn_geometry, {'color': '00FF00'}, 'Drawn Geometry')

    # Save the drawn geometry to a GeoPackage file
    save_drawn_features_as_gpkg(drawn_geometry, file_path)

    # Display the map with the drawn geometry
    Map

# Manually programming a geometry based on coordinates
def manual_func(coords, zoom_level=8):
    # Create an interactive map
    Map = geemap.Map()

    # Manually program a rectangle geometry based on coordinates
    rectangle_geometry = ee.Geometry.Rectangle(coords)

    # Display the manually programmed geometry on the map
    Map.addLayer(rectangle_geometry, {'color': 'FF0000'}, 'Rectangle Geometry')

    # Set the map center and zoom level
    Map.centerObject(rectangle_geometry, zoom=zoom_level)

    # Display the map
    Map

# Manually program a rectangle geometry based on coordinates
manual_func([-122.45, 37.74, -122.4, 37.8])

# Draw a geometry using the drawing tools and store it as a GeoPackage file
draw_geometry('drawn_geometry.gpkg')

# Load the drawn geometry from the saved GeoPackage file
drawn_features = shapefile_to_feature_collection('drawn_geometry.gpkg')

# Visualize datasets clipped to the drawn geometry
visualize_datasets(drawn_features)
