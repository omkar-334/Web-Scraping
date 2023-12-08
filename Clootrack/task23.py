#Task 2 and 3
#Handling Dynamic Content , Data Extraction and Transformation
#I've used the data scraped in task 2 , cleaned it and saved it to a CSV file(task3).

#Importing required libraries and modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
import pandas as pd

#Initialising Driver
edgeService = Service(r"c:\\Users\\omkar\\Downloads\\msedgedriver.exe")
edgeDriver = webdriver.Edge(service=edgeService)
edgeDriver.maximize_window()

edgeDriver.get('https://magicpin.in/New-Delhi/Paharganj/Restaurant/Eatfit/store/61a193/delivery/')
wait = WebDriverWait(edgeDriver, 10)

#Getting the first 5 items of the menu and adding them to the cart
for i in range(5):
    #Waiting till the driver gets all 'add' buttons in the website
    wait.until(EC.presence_of_all_elements_located((By.XPATH, '//button[@class="countCta add "]')))[i].click()
    edgeDriver.implicitly_wait(5)
    try:
        #This option is present if a 'customize you item' menu appears on adding it to the cart
        edgeDriver.find_element(By.XPATH, '//button[@class="addCTA"]').click()
    except:
        pass
    edgeDriver.implicitly_wait(5)

#Names of the items in our cart
names=[i.text for i in edgeDriver.find_elements(By.XPATH,'//div[@class="orderCheckoutItems"]//p[@class="name"]')]
edgeDriver.implicitly_wait(5)

#Prices of the items in our cart
prices=[i.text.replace("\n","") for i in edgeDriver.find_elements(By.XPATH,'//div[@class="orderCheckoutItems"]//span[@class="price"]')]
edgeDriver.implicitly_wait(5)

#Getting the total price, savings and the final price.
total=edgeDriver.find_element(By.XPATH,'//span[@class="highPrice"]').text
final=edgeDriver.find_element(By.XPATH,'//span[@class="finalPrice"]').text
savings=edgeDriver.find_element(By.XPATH,'//span[@class="savingPrice"]').text
edgeDriver.implicitly_wait(5)

#Seperating the Price and the quantity of the items
quantity=[i[5:] for i in prices]
prices=[i[:4] for i in prices]

#Creating a pandas dataframe and writing it to a csv file
df=pd.DataFrame({"Name":names,"Price":prices,"Quantity":quantity})
df.to_csv('output.csv')

#Printing the total price, davings and final price.
print(f"Total Price - {total}")
print(f"{savings}\n")
print(f"Final Price - {final}")

edgeDriver.quit()

