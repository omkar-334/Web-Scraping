import re
import codecs
import pandas as pd
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

options = Options()
options.add_argument("--headless=new") 
edgeService = Service(r"c:\\Users\\omkar\\Downloads\\msedgedriver.exe")
edgeDriver = webdriver.Edge(service=edgeService,options=options)
edgeDriver.maximize_window()

df=pd.DataFrame({"Name":[],"Address":[],"Contact":[],"Max Discount":[],"Link":[]})

text=codecs.open("sourcecode.txt",encoding='utf-8')
text="".join(text.readlines())
out=re.findall(r'href="/chennai.*\b',text)

defurl="https://www.nearbuy.com"

links=list(set([defurl+i[6:] for i in out]))


for idx,url in enumerate(links):
    site=requests.get(url)
    soup=BeautifulSoup(site.content,"html.parser")
    try:
        name=soup.find("p",attrs={"class":"font-weight-ebold txt-capitalize txt-primary font-4xl line-height-md"}).text
        address=soup.find("span",attrs={"class":"txt-secondary font-xl line-height-default margin-right-s"}).text
        contact=soup.find_all("div",attrs={"class":"margin-bottom-l"})[1].find("p").text

        itemsurl=url+"#deals"
        edgeDriver.get(itemsurl)
        wait = WebDriverWait(edgeDriver, 10)
        items=wait.until(EC.presence_of_all_elements_located((By.XPATH, '//p[@class="tag tag--small tag--border txt-delight-8 margin-bottom-zero font-weight-semibold line-height-default"]')))
        edgeDriver.implicitly_wait(5)
        discount=max([int(i.text[:-5]) for i in items])
        print(idx)
        print("===")

        df.loc[idx]=[name,address,contact,discount,itemsurl]
    except:
        pass

print(df.head())
df.to_csv("nearbuy.csv")
