# @Author: Shounak Ray <Ray>
# @Date:   02-May-2021 16:05:52:521  GMT-0600
# @Email:  rijshouray@gmail.com
# @Filename: scrape_files.py
# @Last modified by:   Ray
# @Last modified time: 04-May-2021 22:05:83:831  GMT-0600
# @License: MIT License


import ast

import _references._accessories as _accessories
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from selenium.webdriver.chrome.options import Options

_accessories._print('Dependencies imported.')

_ = """
#######################################################################################################################
#############################################   NOTES AND ASSUMPTIONS   ###############################################
#######################################################################################################################
"""
# 1. The "Index" link for each county is http://mil.library.ucsb.edu/ap_indexes/ followed by the flight idea
#    in all lowercase and without non-alphanumeric characters
# 2. All cells in the "Scale" column for each county is always formatted as "1:[whatever number]"
# 3. The general page structure of each county webpage does not change (relative xpaths are assumed constant)

_ = """
#######################################################################################################################
#################################################   HYPERPARAMTERS   ##################################################
#######################################################################################################################
"""
# This is the URL where the data is located
URL_all_counties = 'https://www.library.ucsb.edu/geospatial/airphotos/california-aerial-photography-county'

_accessories._print('Hyperparameters defined.')

_ = """
#######################################################################################################################
################################################   LOCAL DEFINITIONS   ################################################
#######################################################################################################################
"""

_accessories._print('Local functions defined.')

_ = """
#######################################################################################################################
###############################################  CENTROID LOCATIONS   #################################################
#######################################################################################################################
"""
tiles_df = pd.read_csv('Data/All_Flights_Merge_4tiles.csv').infer_objects()
tiles_df.columns = ['long', 'lat', 'FID_delete', 'object_id', 'held_delete', 'flight_id', 'date',
                    'frame', 'scale', 'latlong_delete', 'scan', 'roll_delete', 'nitrate_delete',
                    'cut_frame_delete', 'print_delete']
tiles_df = tiles_df[[c for c in tiles_df.columns if '_delete' not in c]]
tiles_df['scan'] = tiles_df['scan'].str.extract('(http:\S+.tif)')
tiles_df['date'] = pd.to_datetime(tiles_df['date'])

raw_df = pd.read_csv('Data/All_Flights_Merge.csv').infer_objects()
raw_df.columns = ['long', 'lat', 'FID_delete', 'object_id', 'held_delete', 'flight_id', 'date',
                  'frame', 'scale', 'latlong_delete', 'scan', 'roll_delete', 'nitrate_delete',
                  'cut_frame_delete', 'print_delete']
raw_df = raw_df[[c for c in raw_df.columns if '_delete' not in c]]
raw_df['scan'] = raw_df['scan'].str.extract('(http:\S+.tif)')
raw_df['date'] = pd.to_datetime(raw_df['date'])

_temp = raw_df[(raw_df['long'] < -110) & (raw_df['lat'] > 31)].reset_index(drop=True)
plt.figure(figsize=(40, 40))
figure = sns.scatterplot(data=_temp, x='long', y='lat', hue='flight_id', legend=False)
figure.set_title('Latitude VS. Longitude for Selective Flight Paths')
figure.get_figure().savefig('Images/trimmed_flight_paths.png', dpi=144, bbox_inches='tight')

_temp = raw_df[(raw_df['long'] < -110) & (raw_df['lat'] > 31)].reset_index(drop=True)
date_info = _temp['date'].apply(lambda x: x.date().year) - min(_temp['date']).date().year
ax = Axes3D(plt.figure())
ax.plot_trisurf(_temp['long'], _temp['lat'], date_info)


_ = """
#######################################################################################################################
#################################################  SCRAPING SETUP   ###################################################
#######################################################################################################################
"""
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--kiosk")
driver = _accessories.init_driver(chrome_options)

_accessories._print('Setup complete.')

_ = """
#######################################################################################################################
#################################################   INITIAL SCRAPE   ##################################################
#######################################################################################################################
"""
_accessories.load(driver, URL_all_counties, val_xpath='//*[@id="content"]/article/div/h3')

counties_obj = driver.find_element_by_xpath('//*[@id="content"]/article/div/ul').find_elements_by_tag_name('li')
county_names = {elem.find_element_by_tag_name('a').text: elem.find_element_by_tag_name('a').get_attribute('href')
                for elem in counties_obj}

all_data = []
for county, county_url in county_names.items():
    try:
        # Open a new, temporary tab and load the respective url for the current county
        _accessories._print(f'Processing "{county}" at "{county_url}"...', color='GREEN')
        _accessories.open_tab(driver)
        _accessories.load(driver, county_url, val_xpath=None)

        # Get the specified table on the page
        # NOTE: Exceptions are specifically caught here since the UCSB website sometimes timesout.
        #       This may be due to multiple requests or bad internet connection. The page is refreshed to hopefully
        #       fix this issue. If this error still persists, scraping will stop as an Exception will be raised.
        try:
            table = pd.read_html(driver.find_element_by_xpath(
                '/html/body/div[5]/table').get_attribute('outerHTML'))[0]
        except Exception:
            _accessories._print('The page was not read properly the first time, refreshing...', color='LIGHTRED_EX')
            driver.refresh()
            table = pd.read_html(driver.find_element_by_xpath(
                '/html/body/div[5]/table').get_attribute('outerHTML'))[0]

        # Minor data cleaning
        table.drop([0, 1], axis=0, inplace=True)
        table.columns = ['date', 'flight_id', 'scale', 'index_url', 'frame_status']
        table['date'] = pd.to_datetime(table['date'], errors='coerce')

        # Feature addition/formatting
        table['index_url'] = table['flight_id'].apply(lambda x:
                                                      'http://mil.library.ucsb.edu/ap_indexes/' +
                                                      x.replace('-', '').lower())
        table['scale'] = [[v.replace(',', '') for v in found if v != '']
                          for found in table['scale'].str.split('1:').replace(np.nan, '')]
        table['reference_image_url'] = driver.find_element_by_xpath(
            '/html/body/div[4]/table/tbody/tr/td[2]/img').get_attribute('src')
        table['county_name'] = county
        table['county_url'] = county_url

        # Store the data in each run
        all_data.append(table)
        _accessories.close_tab(driver)
    except Exception as e:
        # If something ever goes wrong (except the read_html part), then skips and keep going...
        _accessories._print(f'Something went wrong! {e[:100]}\n Proceeding...', color='LIGHTRED_EX')

# Concatenate all the data and save it
surface_level_data = pd.concat(all_data).reset_index(drop=True).infer_objects()
_accessories.auto_make_path('Data/')
_accessories.save_local_data_file(surface_level_data, 'Data/surface_level.csv')

_accessories._print('Scraped county surface-level data and saved to file.')

surface_level_data = _accessories.retrieve_local_data_file('Data/surface_level.csv')
surface_level_data['scale'] = [ast.literal_eval(val) for val in surface_level_data['scale']]

_ = """
#######################################################################################################################
#################################################   DEEPER SCRAPE   ###################################################
#######################################################################################################################
"""

_ = """
#######################################################################################################################
#######################################   MERGED SCRAPED AND DOWNLOADED DATA   ########################################
#######################################################################################################################
"""

surface_level_data['scale'] = surface_level_data['scale'].apply(lambda x: x[0] if len(x) == 1 else x)
surface_level_data = surface_level_data[surface_level_data['scale'].apply(lambda x: str(x).isdigit())].infer_objects()
surface_level_data['date'] = pd.to_datetime(surface_level_data['date'], errors='coerce', utc=True)
surface_level_data.dtypes

pd.merge(raw_df, surface_level_data, how='outer', on=['date', 'flight_id'])

driver.quit()

# EOF

# EOF
