import requests
import pandas as pd
from selenium.webdriver import EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from seleniumwire import webdriver
    
def create_driver(self):
    options = EdgeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('log-level=3')
    # options.add_argument('--allow-running-insecure-content')
    # options.add_argument('--ignore-certificate-errors')
    options.add_argument("user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/122.0.2365.92")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    prefs = {"profile.default_content_settings.popups": 0,    
            "download.default_directory":r"C:\Users\omkar\Desktop\NSDL",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Edge(options = options)
    # print(driver.capabilities['browserVersion'])
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/122.0.2365.92'})
    return driver

def get_table(url):
    driver = create_driver()
    driver.get(url)
    wait = WebDriverWait(driver,30)
    try:
        tablecode = wait.until(EC.presence_of_element_located((By.XPATH, '//react-continuous-prediction-table'))).get_attribute('innerHTML')

        table = pd.read_html(StringIO(str(tablecode)))[0]
    except Exception as e:
        print(e)
        return None
    # rcfp = wait.until(EC.presence_of_element_located((By .XPATH, '//div[@class="content prediction-section-resolution-criteria"]'))).get_attribute('innerText')
    # bginfo = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="content font-sans [&>:first-child]:mt-0 [&>:last-child]:mb-0"]'))).get_attribute('innerText')
    driver.close()
    return table


x = requests.get('https://www.metaculus.com/api2/questions/?limit=100&offset=0&topic=ai&status=closed').json()['results']
cdf = pd.DataFrame(x)[['url','page_url', 'title']]
x = requests.get('https://www.metaculus.com/api2/questions/?limit=100&offset=0&topic=ai&status=resolved').json()['results']
rdf = pd.DataFrame(x)[['url','page_url', 'title']]
cdf['page_url'] = 'https://www.metaculus.com' + cdf['page_url']
rdf['page_url'] = 'https://www.metaculus.com' + rdf['page_url']

def get_out(url):
    x = requests.get(url).json()
    return [x.get('description'), x.get('resolution_criteria'), x.get('fine_print')]

cdf['out'] = cdf['url'].apply(get_out)
rdf['out'] = rdf['url'].apply(get_out)
cdf[['desc','resc','fp']] = cdf['out'].to_list()
rdf[['desc','resc','fp']] = rdf['out'].to_list()
cdf['table'] = cdf['page_url'].apply(get_table)
rdf['table'] = rdf['page_url'].apply(get_table)
