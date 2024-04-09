from io import StringIO
import time
import os

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver

def create_driver(self):
    options = ChromeOptions()
    # options.add_argument('--allow-running-insecure-content')
    # options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('log-level=3')
    options.add_argument("user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    prefs = {"profile.default_content_settings.popups": 0,    
            "download.default_directory":os.getcwd(),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/122.0.2365.92'})
    return driver

def get_announcements(self, symbol : str = None, tab : str = 'Equity'):
    if symbol is None:
        url = 'https://www.nseindia.com/companies-listing/corporate-filings-announcements'
    else:
        url = f'https://www.nseindia.com/companies-listing/corporate-filings-announcements?symbol={symbol}&tabIndex={tab}'

    driver = self.create_driver()
    driver.get(url)
    driver.maximize_window()
    time.sleep(10)
    wait = WebDriverWait(driver,30)
    
    # inpute = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="Announcements_equity"]/div[1]/div[1]/div/span/input'))).send_keys(symbol)
    # driver.implicitly_wait(5)

    if symbol is None:
        week = wait.until(EC.presence_of_element_located((By.XPATH, '(//a[@data-val="1W"])')))
        driver.execute_script("arguments[0].click();",week)
        driver.implicitly_wait(10)
        
    xpath = f'(//table[@id="CFannc{tab}Table"]/tbody/tr)[last()]'

    row1 = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        
    driver.execute_script("arguments[0].click();",row1)
    act = ActionChains(driver)
    act.move_to_element(row1).click()
    act.send_keys(Keys.PAGE_DOWN).perform()
    time.sleep(10)
    src = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(src, 'lxml').find('table', id=id)
    for div in soup.find_all("div", {'class':'hover_table'}): 
        div.decompose()
    df = pd.read_html(StringIO(str(soup)), extract_links='body')[0]
    df = df.apply(lambda col: [v[1] if not v[0] else v[0] for v in  col])
    df = df.drop_duplicates()
    return df        

def get_Nsme(self):
    nseurl = 'https://www.nseindia.com/market-data/sme-market'
    
    driver = self.create_driver()
    driver.get(nseurl)
    time.sleep(10)
    wait = WebDriverWait(driver,30)

    row1 = wait.until(EC.presence_of_element_located((By.XPATH, '(//table[@id="liveSMEkTable"]/tbody/tr)[last()]')))
    driver.execute_script("arguments[0].click();",row1)
    act = ActionChains(driver)
    act.move_to_element(row1).click()
    act.send_keys(Keys.PAGE_DOWN).perform()
    time.sleep(10)
    src = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(src, 'lxml').find('table')
    for div in soup.find_all("div", {'class':'hover_table'}): 
        div.decompose()
    df = pd.read_html(StringIO(str(soup)), extract_links='body')[0]
    df = df.apply(lambda col: [v[1] if not v[0] else v[0] for v in  col])
    df = df.drop_duplicates()
    return df
