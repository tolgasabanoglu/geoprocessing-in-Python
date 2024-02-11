# paths to raster and vector files
disturbance_raster_path = '/Users/tolgasabanoglu/Desktop/geoinpython/forest_disturbance/disturbance_year_1986-2020_slovakia.tif'
nuts_vector_path = '/Users/tolgasabanoglu/Desktop/geoinpython/forest_disturbance/NUTS_RG_01M_2021_3035_sk3.gpkg'

# read vector data
nuts_data = gpd.read_file(nuts_vector_path)

# read raster data
disturbance_raster = rasterio.open(disturbance_raster_path)

# calculate the pixel area in square meters
pixel_area = disturbance_raster.res[0] ** 2

# initialize a DataFrame to store the area statistics
area_statistics = pd.DataFrame(columns=['nuts_id', 'year', 'disturbed_area'])

# iterate over each year in the disturbance raster
for year in range(1986, 2021):
    # create a mask for the current year
    mask = (disturbance_raster.read(1) == year)
    
    # iterate over each NUTS-3 region
    for index, region in nuts_data.iterrows():
        # extract the geometry of the region
        geometry = region['geometry']
        
        # create a mask for the current region
        region_mask = geometry_mask([geometry], out_shape=mask.shape, transform=disturbance_raster.transform, invert=False)
        
        # calculate the disturbed area for the current region and year
        disturbed_area = np.sum(mask & region_mask) * pixel_area
        
        # append the results to the DataFrame
        area_statistics = pd.concat([area_statistics, pd.DataFrame([[region['id'], year, disturbed_area]], columns=area_statistics.columns)])

# set the DataFrame index
area_statistics.set_index(['nuts_id', 'year'], inplace=True)

# display the first 5 rows of the area statistics
print(area_statistics.head())

# plot a line graph showing disturbed forest area over the years
plt.figure(figsize=(12, 8))
for nuts_id, group in area_statistics.groupby('nuts_id'):
    plt.plot(group.index.get_level_values('year'), group['disturbed_area'], label=f'NUTS-{nuts_id}')

plt.title('Annual Disturbed Forest Area per NUTS-3 Region')
plt.xlabel('Year')
plt.ylabel('Disturbed Area (m^2)')
plt.legend()
plt.show()
