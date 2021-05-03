# @Author: Shounak Ray <Ray>
# @Date:   02-May-2021 17:05:60:607  GMT-0600
# @Email:  rijshouray@gmail.com
# @Filename: _accessories.py
# @Last modified by:   Ray
# @Last modified time: 02-May-2021 20:05:68:688  GMT-0600
# @License: [Private IP]

import ast
import os
import pickle
import time
from io import StringIO

import pandas as pd
# Scraping Libraries
import selenium
from colorama import Fore, Style
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


def open_tab(driver: selenium.webdriver.chrome.webdriver.WebDriver) -> None:
    """Opens a new tab.

    Parameters
    ----------
    driver : selenium.webdriver.chrome.webdriver.WebDriver
        The selenium webdriver programmatically created and used in the main script.

    Returns
    -------
    None
        Nothing is returned, although a string is printed for tracking purposes.

    """
    driver.execute_script("window.open('');")
    driver.switch_to_window(driver.window_handles[-1])
    # _print('New tab opened.', color='CYAN')


def close_tab(driver: selenium.webdriver.chrome.webdriver.WebDriver) -> None:
    """Closes the tab open latest.

    Parameters
    ----------
    driver : selenium.webdriver.chrome.webdriver.WebDriver
        The selenium webdriver programmatically created and used in the main script.

    Returns
    -------
    None
        Nothing is returned, although a string is printed for tracking purposes.

    """
    driver.execute_script("window.close('');")
    driver.switch_to_window(driver.window_handles[-1])
    # _print('Latest tab closed.', color='CYAN')


def util_validate(driver: selenium.webdriver.chrome.webdriver.WebDriver, xpath: str,
                  TIMEOUT_THRESH: int = TIMEOUT_THRESH) -> None:
    """Holds control until specified xpath appears on loaded page – until timeout.

    Parameters
    ----------
    driver : selenium.webdriver.chrome.webdriver.WebDriver
        The selenium webdriver programmatically created and used in the main script.
    xpath : str
        The xpath which should exist on the page once it has fully loaded.
    TIMEOUT_THRESH : type
        How many seconds control should be held before an exception is raised.

    Returns
    -------
    None
        Nothing is returned, although a string is printed for tracking purposes.

    """
    try:
        WebDriverWait(driver, TIMEOUT_THRESH).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        _print('Page timed out after ' + str(TIMEOUT_THRESH) + ' seconds during validation.', color='LIGHTRED_EX')


def load(driver: selenium.webdriver.chrome.webdriver.WebDriver, url: str, val_xpath: str = None,
         TIMEOUT_THRESH: int = TIMEOUT_THRESH, GRACE: int = GRACE) -> None:
    """Load an url on the supplied driver and check if it's loaded properly.

    Parameters
    ----------
    driver : selenium.webdriver.chrome.webdriver.WebDriver
        The selenium webdriver programmatically created and used in the main script.
    url : str
        The url which should be loaded.
    val_xpath : str
        The xpath of the element which should appear once the page is properly loaded.
    TIMEOUT_THRESH : int
        How many seconds control should be held before an exception is raised.
    GRACE : int
        How many seconds control should wait even after the page is loaded [and validated].

    Returns
    -------
    None
        Nothing is returned, although a string is printed for tracking purposes.

    """
    driver.get(url)
    if(val_xpath is not None):
        util_validate(driver, val_xpath)
    time.sleep(GRACE)
    # _print(f'"{url}" loaded...', color='CYAN')


def click(driver: selenium.webdriver.chrome.webdriver.WebDriver, xpath: str = None, val_xpath: str = None,
          TIMEOUT_THRESH: int = TIMEOUT_THRESH) -> None:
    """Click an element given it's xpath.

    Parameters
    ----------
    driver : selenium.webdriver.chrome.webdriver.WebDriver
        The selenium webdriver programmatically created and used in the main script.
    xpath : str
        The xpath of the element which should be clicked.
    val_xpath : str
        The xpath of the element which should appear once the click is properly completed.
    TIMEOUT_THRESH : int
        How many seconds control should be held before an exception is raised.

    Returns
    -------
    None
        Nothing is returned, although a string is printed for tracking purposes.

    """
    driver.find_element_by_xpath(xpath).click()
    if(val_xpath is not None):
        util_validate(driver, val_xpath)

    # _print(f'Element clicked at "{xpath}"', color='CYAN')


def sel_type(driver: selenium.webdriver.chrome.webdriver.WebDriver, content: str, xpath: str,
             GRACE: int = GRACE) -> None:
    """Type something.

    Parameters
    ----------
    driver : selenium.webdriver.chrome.webdriver.WebDriver
        The selenium webdriver programmatically created and used in the main script.
    content : str
        What should be typed.
    xpath : str
        The xpath of the element where `content` should be typed.
    GRACE : int
        How many seconds control should wait even after the content is typed.

    Returns
    -------
    None
        Nothing is returned, although a string is printed for tracking purposes.

    """
    elem = driver.find_element_by_xpath(xpath)
    elem.click()
    elem.send_keys(content)
    time.sleep(GRACE)
    # _print(f'"{content}" typed in "{xpath}"', color='CYAN')


def init_driver(options:
                selenium.webdriver.chrome.options.Options = None) -> selenium.webdriver.chrome.webdriver.WebDriver:
    """Initialize a driver [given chrome options].

    Parameters
    ----------
    options : selenium.webdriver.chrome.options.Options
        The selenium webdriver programmatically created and used in the main script.

    Returns
    -------
    selenium.webdriver.chrome.webdriver.WebDriver
        The selenium webdriver programmatically created and to be used in the main script.

    """
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    # _print('Driver initialized', color='CYAN')
    return driver


_ = """
#######################################################################################################################
############################################   FILE IO + DISPLAY UTILITY   ############################################
#######################################################################################################################
"""


def _print(txt: str, color: str = 'LIGHTGREEN_EX') -> None:
    """Custom print function with optional colored text.

    Parameters
    ----------
    txt : str
        The content of the print statement (must be a text, not any other data structure).
    color : str
        The desired color of the message. This must be compatible with the colorama.Fore package.
        SEE: https://pypi.org/project/colorama/

    Returns
    -------
    None
        While nothing is returned, this function prints to the console.

    """
    fcolor = color.upper()
    if(type(txt) == str):
        # Format the provided string
        txt = txt.replace("'", "\\'").replace('"', '\\"')
        output = f'print(Fore.{fcolor} + """{txt}""" + Style.RESET_ALL)'
        # Print the specified string to the console
    else:
        output = f'print(Fore.{fcolor}, {txt}, Style.RESET_ALL)'
    exec(output)


def retrieve_local_data_file(filedir, mode=1):
    data = None
    filename = filedir.split('/')[-1:][0]
    try:
        if(filename.endswith('.csv')):
            data = pd.read_csv(filedir, error_bad_lines=False, warn_bad_lines=False).infer_objects()
        elif(filename.endswith(('.xlsx', '.xls', '.xlsm', '.xlsb', '.odf', '.ods', '.odt'))):
            data = pd.read_excel(filedir).infer_objects()
        elif(filename.endswith('.pkl')):
            if mode == 1:
                data = pickle.load(filedir).infer_objects()
            elif mode == 2:
                with open(filedir, 'rb') as f:
                    data = f.readlines()[0]
                    data = ast.literal_eval(data.decode("utf-8").replace('\n', ''))
            elif mode == 3:
                with open(filedir, 'r') as file:
                    lines = file.readlines()
                    data = pd.read_csv(StringIO(''.join(lines)), delim_whitespace=True).infer_objects()
        if(data is None):
            raise Exception
        _print(f'> Imported "{filename}"...', color='GREEN')
    except Exception as e:
        _print('Unable to retrieve local data', color='RED')
        raise e
    return data


def save_local_data_file(data, filepath, **kwargs):
    auto_make_path(filepath)
    data = data.infer_objects()
    if(filepath.endswith('.csv')):
        data.to_csv(filepath, index=kwargs.get('index'))
    elif(filepath.endswith('.pkl')):
        with open(filepath, 'w') as file:
            file.write(data)
    _print(f'> Saved data to "{filepath}"', color='GREEN')


def auto_make_path(path: str, **kwargs: bool) -> None:
    """Create the specified directories and nested file. Custom actions based on **kwargs.

    Parameters
    ----------
    path : str
        The path containing [optional] directories and the file name with extenstion.
        Should not begin with backslash.
    **kwargs : bool
        Any keyword arguments to be processed inside `auto_make_path`.

    Returns
    -------
    None
        While nothing is returned, this function makes and [potentially] prints to a file.

    """
    # Sequentially create the directories and files specified in `path`, respectively
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if('.' in path):
        open(path, 'a').close()
    # Confirm creation (waterfall)
    if not os.path.exists(path=path):
        raise Exception('Something is TERRIBLY wrong.')
    _print(f'>> Created: \"{path}\"', color='green')


# EOF

# EOF
