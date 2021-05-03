# @Author: Shounak Ray <Ray>
# @Date:   02-May-2021 16:05:52:521  GMT-0600
# @Email:  rijshouray@gmail.com
# @Filename: scrape_files.py
# @Last modified by:   Ray
# @Last modified time: 02-May-2021 20:05:45:453  GMT-0600
# @License: MIT License


import _references._accessories as _accessories
import numpy as np
import pandas as pd
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
#####################################################   SETUP   #######################################################
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
        table.columns = ['begin_date', 'flight_id', 'scale', 'index_url', 'frame_status']

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
all_data = pd.concat(all_data).reset_index(drop=True).infer_objects()
_accessories.auto_make_path('Data/')
_accessories.save_local_data_file(all_data, 'Data/surface_level.csv')

_accessories._print('Scraped county surface-level data and saved to file.')

# data = _accessories.retrieve_local_data_file('Data/surface_level.csv')

_ = """
#######################################################################################################################
#################################################   DEEPER SCRAPE   ###################################################
#######################################################################################################################
"""

driver.quit()

# EOF

# EOF
