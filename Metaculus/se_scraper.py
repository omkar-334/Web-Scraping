import requests
import time
import pandas as pd
from selenium.webdriver import EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from io import StringIO
from seleniumwire import webdriver
import lxml
    
def create_driver():
    options = EdgeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Edge(options = options)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/122.0.2365.92'})
    return driver

def se_predict(url):
    driver = create_driver()
    driver.get(url)
    wait = WebDriverWait(driver,20)
    try:
        # type = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="bg-metac-blue-400 px-1.5 py-1 font-bold uppercase text-metac-blue-700 dark:bg-metac-blue-400-dark dark:text-metac-blue-700-dark"]'))).get_attribute('innerText')
        type = driver.find_element(By.CSS_SELECTOR, 'body > div.flex.flex-col.w-full.max-w-max.my-16.mx-auto.ng-scope > div.flex.items-start.gap-3.bg-metac-gray-0.px-1.pt-1.dark\:bg-metac-gray-0-dark.xs\:px-3.xs\:pt-3.lg\:bg-transparent.lg\:p-0.lg\:dark\:bg-transparent > span').get_attribute('innerText')

        if type == 'QUESTION':
            # Binary
            out1 = driver.find_element(By.CSS_SELECTOR, 'react-timeseries-stats').get_attribute('innerText')
            # Numerical, Date
            try:
                element2 = driver.find_element(By.XPATH, '//react-continuous-prediction-table')
            except:
                element2 = None
        
        elif type == 'QUESTION GROUP':
            try:
                element1 = driver.find_element(By.XPATH, '//react-multi-binary-prediction-table').get_attribute('innerHTML')
            except NoSuchElementException:
                element1 = driver.find_element(By.XPATH, '//continuous-group-prediction-control').get_attribute('innerHTML')
            
            out1 = pd.read_html(StringIO(str(element1)))[0].iloc[:, :2].dropna().reset_index(drop=True)
            try:
                element2 = driver.find_element(By.XPATH, '//react-continuous-prediction-table')
            except:
                element2 = None
        
        elif type == 'MULTIPLE CHOICE':
            element1 = driver.find_element(By.XPATH, '//react-multiple-choice-prediction-section').get_attribute('innerHTML')
            out1 = pd.read_html(StringIO(str(element1)))[0].iloc[:, :2].dropna().reset_index(drop=True)
            element2 = None
            
        elif type == 'CONDITIONAL PAIR':
            out1 = driver.find_element(By.XPATH, '//react-conditional-summary').get_attribute('innerText')
            try:
                element2 = driver.find_element(By.XPATH, '//react-continuous-prediction-table')
            except:
                element2 = None

        time.sleep(10)   
        if element2:
            out2 = pd.read_html(StringIO(str(element2.get_attribute('innerHTML'))))[0]
            if 'my Prediction' in out2.columns:
                out2 = out2.drop(columns=['My Prediction'])
        else:
            out2 = None

        driver.close() 
        print(type, "success")
        return out1, out2

    except:
        driver.close()
        return None, None
    # rcfp = wait.until(EC.presence_of_element_located((By .XPATH, '//div[@class="content prediction-section-resolution-criteria"]'))).get_attribute('innerText')
    # bginfo = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="content font-sans [&>:first-child]:mt-0 [&>:last-child]:mb-0"]'))).get_attribute('innerText')
    
def get_questions(category, status):
    jsonlist = []
    url = f'https://www.metaculus.com/api2/questions/?limit=100&offset=0&categories={category}&status={status}'

    while url:
        response = requests.get(url).json()
        jsonlist.extend(response['results'])
        url = response['next']
    
    print('json done')
    df = pd.DataFrame(jsonlist)[['url','page_url', 'title', 'close_time']]
    df['page_url'] = 'https://www.metaculus.com' + df['page_url']
    
    return df
    

def get_info(url):
    try:
        x = requests.get(url).json()
        return x.get('description'), x.get('resolution_criteria'), x.get('fine_print')
    except:
        return None, None, None

def df_to_json(df):
    if df is None:
        return None
    else:
        return df.to_json(orient='records')
    
def scrape(category : str, status : str):
    '''status - open, resolved, active, upcoming'''
    df = get_questions(category, status)
    
    df['desc'], df['resc'], df['fp'] = zip(*df['url'].apply(get_info))
    print('Getout done')
    
    df['pred1'], df['pred2'] = zip(*df['page_url'].apply(se_predict))
    # df = df.dropna(subset=['pred1'])

    df.to_csv(f"{category}_{status}.csv")
    df.to_excel(f"{category}_{status}.xlsx")
    return df


def repeat_check(df, alldf):
    newdf = df[~df['url'].isin(alldf['url'])]
    return newdf
