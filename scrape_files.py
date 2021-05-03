# @Author: Shounak Ray <Ray>
# @Date:   02-May-2021 16:05:52:521  GMT-0600
# @Email:  rijshouray@gmail.com
# @Filename: scrape_files.py
# @Last modified by:   Ray
# @Last modified time: 02-May-2021 18:05:64:644  GMT-0600
# @License: MIT License


import _references._accessories as _accessories
import bs4
import numpy as np
import pandas as pd
from selenium.webdriver.chrome.options import Options

_ = """
#######################################################################################################################
#############################################   NOTES AND ASSUMPTIONS   ###############################################
#######################################################################################################################
"""
# 1. The "Index" link for each county is http://mil.library.ucsb.edu/ap_indexes/ followed by the flight idea
#    in all lowercase and without non-alphanumeric characters
# 2. All cells in the "Scale" column for each county is always formatted as "1:[whatever number]"


_ = """
#######################################################################################################################
#################################################   HYPERPARAMTERS   ##################################################
#######################################################################################################################
"""
URL_all_counties = 'https://www.library.ucsb.edu/geospatial/airphotos/california-aerial-photography-county'


_ = """
#######################################################################################################################
################################################   LOCAL DEFINITIONS   ################################################
#######################################################################################################################
"""


_ = """
#######################################################################################################################
#####################################################   SETUP   #######################################################
#######################################################################################################################
"""
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--kiosk")
driver = _accessories.init_driver(chrome_options)


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
        print(f'Processing "{county}" at "{county_url}"...')
        _accessories.open_tab(driver)
        _accessories.load(driver, county_url, val_xpath=None)

        table_on_page = pd.read_html(driver.find_element_by_xpath(
            '/html/body/div[5]/table').get_attribute('outerHTML'))[0]
        table_on_page.drop([0, 1], axis=0, inplace=True)
        table_on_page.columns = ['begin_date', 'flight_id', 'scale', 'index_url', 'frame_status']

        table_on_page['index_url'] = table_on_page['flight_id'].apply(lambda x:
                                                                      'http://mil.library.ucsb.edu/ap_indexes/' +
                                                                      x.replace('-', '').lower())
        table_on_page['scale'] = [[v.replace(',', '') for v in found if v != '']
                                  for found in table_on_page['scale'].str.split('1:').replace(np.nan, '')]
        table_on_page['reference_image_url'] = driver.find_element_by_xpath(
            '/html/body/div[4]/table/tbody/tr/td[2]/img').get_attribute('src')
        table_on_page['county_name'] = county
        table_on_page['county_url'] = county_url

        all_data.append(table_on_page.infer_objects())
        _accessories.close_tab(driver)
    except Exception as e:
        print(f'Something went wrong! {e[:100]}\n Proceeding...')

print("Completed all initial scraping...")
all_data = pd.concat(all_data).reset_index(drop=True).infer_objects()


_ = """
#######################################################################################################################
#################################################   DEEPER SCRAPE   ###################################################
#######################################################################################################################
"""

driver.quit()


# EOF

# EOF
