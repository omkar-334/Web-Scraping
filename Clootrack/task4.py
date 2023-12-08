# Task-4
# Proxy Integration and Handling - Stack Overflow's newest questions.

#Importing required libraries
#FreeProxy is a python library that scrapes websites for free proxies.
from fp.fp import FreeProxy
import requests
from itertools import cycle
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

#Creating a UserAgent object to simulate a real user interaction with the website
ua = UserAgent().edge
header={'User-Agent':str(ua)}
# List of rotating proxies

#Creating a list of proxies
proxy_list = [
    FreeProxy(rand=True).get(),
    FreeProxy(rand=True).get(),
    FreeProxy(rand=True).get(),
    FreeProxy(rand=True).get(),
    FreeProxy(rand=True).get()]

proxy_cycle = cycle(proxy_list)

url=r"https://stackoverflow.com/questions?page={}&sort=newest"
retries = 10

def main():
    for _ in range(retries):
        #Getting the next proxy in the cycle
        proxy = next(proxy_cycle)
        print(proxy)

        try:
            response = requests.get(url, proxies={'http': proxy, 'https': proxy},headers=header)
            soup = BeautifulSoup(response.text, 'lxml')
            #Scraping all questions in the page
            for items in soup.select(".question-hyperlink"):
                print(items.text)
            break

        except requests.RequestException as e:
            print(f"Error: {e}")
            print("Retrying with a new proxy",end='\n\n')
            time.sleep(1)

if __name__ == "__main__":
    main()
