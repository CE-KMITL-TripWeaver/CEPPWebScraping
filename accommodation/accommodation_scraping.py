from bs4 import BeautifulSoup
from selenium import webdriver
import pyautogui
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
import re

# from .interface.accommodation import Accommodation

#edge_driver_path = "D:\XSectorZ\GitHubRepoes\CEPPTravelScraping\CEPPWebScraping\msedgedriver.exe"
#service = Service(executable_path=edge_driver_path)
driver = webdriver.Chrome()

# this url when you search "ที่พักในราชบุรี"
url = "https://www.google.com/maps/search/%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%9E%E0%B8%B1%E0%B8%81%E0%B9%83%E0%B8%99%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/@13.598707,99.7573342,14z/data=!4m4!2m3!5m2!5m1!1s2024-02-12?entry=ttu"
driver.get(url)
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'hfpxzc')))
list_card = driver.find_elements(By.CLASS_NAME, "hfpxzc")
print('first length list_card -> {0}'.format(len(list_card)))
action = ActionChains(driver)
max_length = 0

# use while true if want to get all
while len(list_card) < 20:
    print(len(list_card))
    var = len(list_card)

    scroll_origin = ScrollOrigin.from_element(list_card[len(list_card)-1])
    action.scroll_from_origin(scroll_origin, 0, 1000).perform()
    time.sleep(2)
    list_card = driver.find_elements(By.CLASS_NAME, "hfpxzc")

    if var == len(list_card):
        max_length+=1
        if max_length > 2:
            # check if there is no more div element to scroll
            break
    else:
        max_length = 0

print("length of list_card -> {0}".format(len(list_card)))
# print("all list_card : ")
# print(list_card)
print("**************************************************")

for i in range(len(list_card)):
    # accommodationData = Accommodation()
    scroll_origin = ScrollOrigin.from_element(list_card[i])
    action.scroll_from_origin(scroll_origin, 0, 100).perform()
    action.move_to_element(list_card[i]).perform()
    list_card[i].click()
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # find name
    # accommodationData.name = soup.find_all('h1', class_='DUwDvf lfPIob')
  
    # find imagePath
    img_button = soup.find_all('button', class_='aoRNLd kn2E5e NMjTrf lvtCsd')
    img_tag = None
    img_url = "No Image URL"
    if(len(img_button)):
        img_tag = img_button[0].find('img')
        img_url = img_tag.get('src')

    time.sleep(3)

    # find facilities
        
    # find location data -> (address, province, district, sub district,postcode)
    addressElement = soup.find_all('div', "Io6YTe fontBodyMedium kR99db")
    address= ""
    if(len(addressElement)):
        # accommodationData.location.address = addressElement[0].text
        address = addressElement[0].text
   
    # find rating data (score, rating)
    

    # find star
    
    
    # find contact
    contactElement = soup.find_all('div', "Io6YTe fontBodyMedium kR99db")
    contact = ""
    if(len(contactElement)):
        patternPhone = re.compile(r'\d{3} \d{3} \d{4}')
        patternPhoneService = re.compile(r'\d{3} \d{3} \d{3}')
        for item in contactElement:
            if(re.match(patternPhone,item.text) or re.match(patternPhoneService,item.text)):
                # accommodationData.contact = contactElement[0].text
                contact = item.text
                break

    # find minPrice
    minPriceElement = soup.find_all('div', "pUBf3e oiQUX")
    minPrice = ""
    if(len(minPriceElement)):
        # accommodationData.minPrice = minPriceElement[0].text
        minPrice = minPriceElement[0].text.split('฿')[1].strip()

    # cal latitude, longitude
    start_index_lat = driver.current_url.find("!3d") + 3
    end_index_lat = driver.current_url.find("!4d")
    lat = driver.current_url[start_index_lat:end_index_lat]
    start_index_long = driver.current_url.find("!4d") + 3
    end_index_long = driver.current_url.find("!15s")
    long = driver.current_url[start_index_long:end_index_long]
    
    name = soup.find_all('h1', class_='DUwDvf lfPIob')
    # print(name[0]['class'])
    print('name: {0}'.format(name[0].text))
    print('imagePath: {0}'.format(img_url))
    print('address: {0}'.format(address))
    print('contact: {0}'.format(contact))
    print('minPrice: {0}'.format(minPrice))
    print('LOCATION: {0}, {1}'.format(lat,long))

    # display with object
    # print('name: {0}'.format(accommodationData.name))
    # print('imagePath: {0}'.format(accommodationData.imgPath))
    # print('LOCATION: {0}, {1}'.format(lat,long))
    print("---------------------------")
#soup = BeautifulSoup(driver.page_source, 'html.parser')
#card_elements = soup.find_all('div', class_='wrap-default-cards-articles')

#for card in card_elements:
#    attraction_name = card.find('div', class_='card-title').text.strip()
#    print(attraction_name)

while(True):
    pass