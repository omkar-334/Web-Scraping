#Task1
#Scrape the Magicpin website section to extract the food menu and price details.

#Importing required libraries
import requests
from bs4 import BeautifulSoup

url="https://magicpin.in/New-Delhi/Paharganj/Restaurant/Eatfit/store/61a193/delivery/"
site=requests.get(url)

#Initialising beautifulsoup object
soup=BeautifulSoup(site.content,"html.parser")

#Finding all 'article' elements with class 'categoryListing'
categories=soup.find_all('article',attrs={'class':'categoryListing'})

#Looping through the 'article' elements
for i in categories:
    #Category title name
    title=i.find('h4',attrs={'class':'categoryHeading'}).text

    #List of all items of that category
    items=[j.text for j in i.find_all('a',attrs={'class':'itemName'})]

    #List of all prices of the category
    prices=[k.text for k in i.find_all('span',attrs={'class':'itemPrice'})]

    #Printing the menu
    print(f"Category - {title}")
    print(*(a+"  -  "+b for a,b in zip(items,prices)),sep='\n')
    print("")