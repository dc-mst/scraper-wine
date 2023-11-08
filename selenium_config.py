from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

def setup_vivino(url):
    # Determine the path to chromedriver
    current_directory = os.path.dirname(os.path.realpath(__file__))
    chromedriver_path = os.path.join(current_directory, 'chromedriver')

    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument(f'--binary-location={chromedriver_path}')

    browser = webdriver.Chrome(options=chrome_options)

    # Use Selenium to access the URL
    browser.get(url)
    
    return browser