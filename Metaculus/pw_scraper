import time
from playwright.sync_api import sync_playwright

import requests
import pandas as pd
from io import StringIO

def get_info(url):
    try:
        x = requests.get(url).json()
        return x.get('description'), x.get('resolution_criteria'), x.get('fine_print')
    except:
        return None, None, None
    
defcat = ['artificial intelligence', 'computing and math', 'cryptocurrencies', 'economy & business', 'elections', 'environment & climate', 'geopolitics', 'health & pandemics', 'law', 'metaculus', 'natural sciences', 'nuclear technology & risks', 'politics', 'social sciences', 'space', 'sports & entertainment', 'technology']

def sync_predict(url) -> tuple:
    try:
        with sync_playwright() as p:
            temp = url.rsplit('/', maxsplit=2)[0]
            apiurl = temp[:26] + 'api2/' + temp[26:]
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            
            type = page.locator('css=body > div.flex.flex-col.w-full.max-w-max.my-16.mx-auto.ng-scope > div.flex.items-start.gap-3.bg-metac-gray-0.px-1.pt-1.dark\:bg-metac-gray-0-dark.xs\:px-3.xs\:pt-3.lg\:bg-transparent.lg\:p-0.lg\:dark\:bg-transparent > span').evaluate("el => el.innerText") 
            
            categories = page.get_by_role("button", name="Submit Tags Feedback").evaluate("el => el.parentNode.firstChild.innerText").split('\n')
            test = [i.lower() for i in categories]
            categories = [i for i in test if i in defcat]

            if type =='QUESTION':
                out1 = page.get_by_text('Total Forecasters').evaluate("el => el.parentNode.parentNode.innerText") 
                try:
                    element2 = page.get_by_role('table').evaluate(" el => el.outerHTML")
                except:
                    element2 = None
                    
            elif type == 'QUESTION GROUP':
                    element1 = page.get_by_role('table').all()[0].evaluate(" el => el.outerHTML")
                    out1 = pd.read_html(StringIO(str(element1)))[0].iloc[:, :2].dropna().reset_index(drop=True)
                    
                    try:
                        element2 = page.get_by_role('table').all()[1].evaluate(" el => el.outerHTML")
                    except:
                        element2 = None
                    
            elif type == "MULTIPLE CHOICE":
                element1 = page.get_by_role('table').all()[0].evaluate(" el => el.outerHTML")
                out1 = pd.read_html(StringIO(str(element1)))[0].iloc[:, :2].dropna().reset_index(drop=True)
                element2 = None
            
            elif type == 'CONDITIONAL PAIR':
                element1 = page.get_by_text('if yes', exact=True).evaluate("el => el.parentNode.parentNode.parentNode.parentNode.innerText")
                words = element1.split('\n')
                out1 = words[1] + '\n' + words[2] + ', ' + words[4] + ' -> ' + words[5]+ '\n' + words[3] + ', ' + words[7] + ' -> ' + words[8]
                try:
                    element2 = page.get_by_role('table').all().evaluate(" el => el.outerHTML")
                except:
                    element2 = None
                    
            if element2:
                out2 = pd.read_html(StringIO(str(element2)))[0]
                if 'My Prediction' in out2.columns:
                    out2 = out2.drop(columns=['My Prediction'])
            else:
                out2 = None
            browser.close()
            desc, resc, fp = (get_info(apiurl))
            return desc, resc, fp, type, categories,  out1, out2
    except:
        return None, None, None, None, None, None, None

def get_questions(status : str, category : str = None):
    jsonlist = []
    url = f'https://www.metaculus.com/api2/questions/?limit=100&offset=0&categories={category}&status={status}'
    if category is None:
        url = f'https://www.metaculus.com/api2/questions/?limit=100&offset=0&status={status}'
    
    while url:
        response = requests.get(url).json()
        jsonlist.extend(response['results'])
        url = response['next']
    
    print('json done')
    df = pd.DataFrame(jsonlist)[['url','page_url', 'title', 'close_time']]
    df['page_url'] = 'https://www.metaculus.com' + df['page_url']
    
    return df

def scrape(status : str, category : str = None, df = None):
    '''status - open, resolved, active, upcoming'''
    if df is None:
        df = get_questions(category, status)
    df['desc'], df['resc'], df['fp'], df['type'], df['categories'], df['pred1'], df['pred2'] = zip(*df['page_url'].apply(sync_predict))
    df.to_csv(f"{category}_{status}.csv")
    df.to_excel(f"{category}_{status}.xlsx")
    return df

if __name__ == "__main__":
    start = time.time()
    opdf = scrape(status='open')
        
    print(time.time()-start)
 
