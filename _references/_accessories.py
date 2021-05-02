# @Author: Shounak Ray <Ray>
# @Date:   02-May-2021 17:05:60:607  GMT-0600
# @Email:  rijshouray@gmail.com
# @Filename: _accessories.py
# @Last modified by:   Ray
# @Last modified time: 02-May-2021 17:05:94:947  GMT-0600
# @License: [Private IP]

import time

# Scraping Libraries
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

_ = """
#######################################################################################################################
###########################################   SCRAPING – HYPERPARAMETERS   ############################################
#######################################################################################################################
"""
TIMEOUT_THRESH = 10
GRACE = 2


_ = """
#######################################################################################################################
###########################################   SCRAPING UTILITY FUNCTIONS   ############################################
#######################################################################################################################
"""


def open_tab(driver):
    driver.execute_script("window.open('');")
    driver.switch_to_window(driver.window_handles[-1])


def close_tab(driver):
    driver.execute_script("window.close('');")
    driver.switch_to_window(driver.window_handles[-1])


def util_validate(driver, xpath, TIMEOUT_THRESH=TIMEOUT_THRESH):
    try:
        WebDriverWait(driver, TIMEOUT_THRESH).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        print('Page timed out after ' + str(TIMEOUT_THRESH) + ' seconds during validation.')


def load(driver, url, val_xpath=None, TIMEOUT_THRESH=TIMEOUT_THRESH, GRACE=GRACE):
    driver.get(url)
    if(val_xpath is not None):
        util_validate(driver, val_xpath)
    time.sleep(GRACE)


def click(driver, xpath=None, val_xpath=None, TIMEOUT_THRESH=TIMEOUT_THRESH):
    driver.find_element_by_xpath(xpath).click()
    if(val_xpath is not None):
        util_validate(driver, val_xpath)


def type(driver, content, xpath, GRACE=GRACE):
    elem = driver.find_element_by_xpath(xpath)
    elem.click()
    elem.send_keys(content)
    time.sleep(GRACE)


def init_driver(options=None):
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver


# EOF

# EOF
