# libraries
import os
import pandas as pd
import numpy as np
from osgeo import gdal
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from multiprocessing import Pool
from functools import partial
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# import geopy_ml_fun as geopy  # Visualize and save map - install it

gdal.UseExceptions()

# create prediction function


def read_band(band_number, input_image):
    print(f"Reading band {band_number}...")
    landsat_tile = gdal.Open(input_image)
    band_data = landsat_tile.GetRasterBand(band_number).ReadAsArray()
    return band_data.flatten()


def process_image_batch(model, input_images, output_folder):
    for i, input_image in enumerate(input_images):
        output_path = os.path.join(
            output_folder, f"land_cover_map_{i}.tif")
        process_image(model, input_image, output_path)


def process_image(model, input_image, output_path):
    from osgeo import gdal
    print("Loading Landsat tile data...")
    landsat_tile = gdal.Open(input_image)

    selected_bands = range(1, 36)
    landsat_data = [read_band(band, input_image) for band in selected_bands]
    landsat_data = pd.DataFrame(landsat_data).T

    print("Applying the trained model to predict land cover...")
    land_cover = model.predict(landsat_data)

    print("Saving the land cover map...")
    driver = gdal.GetDriverByName("GTiff")
    output_ds = driver.Create(
        output_path, landsat_tile.RasterXSize, landsat_tile.RasterYSize, 1, gdal.GDT_Byte)
    output_ds.SetGeoTransform(landsat_tile.GetGeoTransform())
    output_ds.SetProjection(landsat_tile.GetProjection())
    output_ds.GetRasterBand(1).WriteArray(
        land_cover.reshape((landsat_tile.RasterYSize, landsat_tile.RasterXSize)))
    output_ds = None
    print(f"Land cover map saved at {output_path}")

# train and tune the model with best parameters


def main():
    # load reference data
    reference_data = pd.read_csv(
        "/Users/tolgasabanoglu/Desktop/geoinpython/ml/berlin_landsat_sample.csv")

    # define features (spectral-temporal metrics) and target (land cover class)
    X = reference_data.iloc[:, 1:-1]
    y = reference_data["class"]

    # split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    # train and tune RF
    rf = RandomForestClassifier()
    param_grid = {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20, 30]}
    grid_search = GridSearchCV(rf, param_grid, cv=5)
    grid_search.fit(X_train, y_train)

    # print best parameters
    print("Best Parameters:", grid_search.best_params_)

    # evaluate the classification model
    y_pred = grid_search.predict(X_test)
    overall_accuracy = accuracy_score(y_test, y_pred)
    classwise_accuracy = classification_report(y_test, y_pred)

    print("Overall Accuracy:", overall_accuracy)
    print("Class-wise Accuracy:\n", classwise_accuracy)

    # RF with the best parameters
    rf = RandomForestClassifier(**grid_search.best_params_)
    rf.fit(X_train, y_train)

    # evaluate the classification model
    y_pred = rf.predict(X_test)
    overall_accuracy = accuracy_score(y_test, y_pred)
    classwise_accuracy = classification_report(y_test, y_pred)

    print("Overall Accuracy:", overall_accuracy)

    # stm files
    input_images = [
        "/Users/tolgasabanoglu/Desktop/geoinpython/ml/landsat_stm_berlin/X0068_Y0043_landsat_stm_2018.tif",
        "/Users/tolgasabanoglu/Desktop/geoinpython/ml/landsat_stm_berlin/X0068_Y0044_landsat_stm_2018.tif",
        "/Users/tolgasabanoglu/Desktop/geoinpython/ml/landsat_stm_berlin/X0069_Y0043_landsat_stm_2018.tif",
        "/Users/tolgasabanoglu/Desktop/geoinpython/ml/landsat_stm_berlin/X0069_Y0044_landsat_stm_2018.tif",
    ]

    output_folder = "/Users/tolgasabanoglu/Desktop/geoinpython/ml/outputs/machine_learning/"

    # number of processes to use (adjusting based on CPU)
    num_processes = 4

    # batch size for processing images - due to long computation time, I only managed to print 2 output maps
    batch_size = 2

    # create a Pool with the specified number of processes
    with Pool(processes=num_processes) as pool:
        # process the images in batches
        for i in range(0, len(input_images), batch_size):
            batch_input_images = input_images[i:i + batch_size]
            pool.starmap(
                partial(process_image_batch, rf),
                [(batch_input_images, output_folder)]
            )


if __name__ == "__main__":
    main()


# visualize 2 land cover prediction maps

def visualize_land_cover(file_path):
    # load the predicted land cover
    land_cover = gdal.Open(file_path).ReadAsArray()

    # extract unique class labels
    unique_labels = np.unique(land_cover)

    # generate a colormap based on unique class labels
    cmap_colors = plt.cm.get_cmap("tab10", len(unique_labels))
    custom_cmap = ListedColormap(cmap_colors.colors)

    # visualize the predicted land cover with the custom colormap
    plt.imshow(land_cover, cmap=custom_cmap)
    plt.title(f"Predicted Land Cover - {os.path.basename(file_path)}")
    plt.colorbar(ticks=unique_labels, label="Land Cover Class")
    plt.show()


def visualize_outputs(output_folder):
    for file_name in os.listdir(output_folder):
        if file_name.endswith(".tif"):
            file_path = os.path.join(output_folder, file_name)
            visualize_land_cover(file_path)

# replace the path with your output folder
output_folder = "/Users/tolgasabanoglu/Desktop/geoinpython/ml/outputs/machine_learning"
visualize_outputs(output_folder)
