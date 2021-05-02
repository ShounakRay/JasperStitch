# @Author: Shounak Ray <Ray>
# @Date:   02-May-2021 16:05:52:521  GMT-0600
# @Email:  rijshouray@gmail.com
# @Filename: scrape_files.py
# @Last modified by:   Ray
# @Last modified time: 02-May-2021 17:05:18:186  GMT-0600
# @License: MIT License

import _references._accessories as _accessories
import bs4
import pandas as pd
from selenium.webdriver.chrome.options import Options

_ = """
#######################################################################################################################
#############################################   NOTES AND ASSUMPTIONS   ###############################################
#######################################################################################################################
"""
# 1. The "Index" link for each county is http://mil.library.ucsb.edu/ap_indexes/ followed by the flight idea
#    in all lowercase and without non-alphanumeric characters
# 2. All scale options are


_ = """
#######################################################################################################################
#################################################   HYPERPARAMTERS   ##################################################
#######################################################################################################################
"""
URL_all_counties = 'https://www.library.ucsb.edu/geospatial/airphotos/california-aerial-photography-county'

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--kiosk")

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

data_by_county = {}
for county, county_url in county_names.items():
    _accessories.open_tab(driver)
    _accessories.load(driver, county_url, val_xpath='/html/body/div[5]/table')

    table_on_page = pd.read_html(driver.find_element_by_xpath('/html/body/div[5]/table').get_attribute('outerHTML'))[0]
    table_on_page.drop([0, 1], axis=0, inplace=True)
    table_on_page.columns = ['begin_date', 'flight_id', 'scale', 'index_url', 'frame_status']

    table_on_page['index_url'] = table_on_page['flight_id'].apply(lambda x:
                                                                  'http://mil.library.ucsb.edu/ap_indexes/' + x.replace('-', '').lower())
    table_on_page['county_name'] = county
    table_on_page['county_url'] = county_url
    data_by_county[county] = table_on_page.infer_objects()


soup = bs4.BeautifulSoup(driver.page_source)


_ = """
#######################################################################################################################
#################################################   DEEPER SCRAPE   ###################################################
#######################################################################################################################
"""

driver.quit()


# EOF

# EOF
