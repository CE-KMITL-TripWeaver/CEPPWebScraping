from bs4 import BeautifulSoup
from selenium import webdriver
import pyautogui
import re
from bs4 import BeautifulSoup
import time
import pandas as pd
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

edge_driver_path = "D:\XSectorZ\GitHubRepoes\CEPPTravelScraping\CEPPWebScraping\msedgedriver.exe"
service = Service(executable_path=edge_driver_path)
driver = webdriver.Edge(service = service)
#url = "https://thai.tourismthailand.org/Search-result/attraction?destination_id=238&sort_by=datetime_updated_desc&page=1&perpage=15&menu=attraction"
#url = "https://www.google.com/maps/search/%E0%B8%AA%E0%B8%96%E0%B8%B2%E0%B8%99%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%97%E0%B9%88%E0%B8%AD%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%A7%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/@13.5524175,98.9526212,9z/data=!3m1!4b1?entry=ttu"
url = "https://www.google.com/maps/search/%E0%B8%97%E0%B9%88%E0%B8%AD%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%A7%E0%B9%80%E0%B8%82%E0%B8%95%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%99%E0%B8%84%E0%B8%A3/@13.7540829,100.4870287,15z/data=!3m1!4b1?authuser=0&entry=ttu"

driver.get(url)
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'hfpxzc')))
list_card = driver.find_elements(By.CLASS_NAME, "hfpxzc")
action = ActionChains(driver)
max_length = 0

#provice = "ราชบุรี"
provice = "กรุงเทพมหานคร"
df = pd.read_csv("geocode.csv", header=None)

patternPhone = re.compile(r'\d{3} \d{3} \d{4}')
patternPhoneService = re.compile(r'\d{3} \d{3} \d{3}')

subStrDistict = "อำเภอ"
subStrSubDistict = "ตำบล"

if provice == "กรุงเทพมหานคร":
    subStrDistict = "เขต"
    subStrSubDistict = "แขวง"

while len(list_card) < 100:
    print(len(list_card))
    var = len(list_card)

    scroll_origin = ScrollOrigin.from_element(list_card[len(list_card)-1])
    action.scroll_from_origin(scroll_origin, 0, 1000).perform()
    time.sleep(2)
    list_card = driver.find_elements(By.CLASS_NAME, "hfpxzc")

    if var == len(list_card):
        max_length+=1
        if max_length > 2:
            break
    else:
        max_length = 0

for i in range(len(list_card)):
    scroll_origin = ScrollOrigin.from_element(list_card[i])
    action.scroll_from_origin(scroll_origin, 0, 100).perform()
    action.move_to_element(list_card[i]).perform()
    list_card[i].click()

    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    name = soup.find_all('h1', class_='DUwDvf lfPIob')
    description = soup.find_all('div', class_='PYvSYb')
    address = soup.find_all('div', class_='Io6YTe')
    loc = soup.find_all('div', class_='rogA2c')

    time.sleep(3)
    print(name[0].text)
    start_index_lat = driver.current_url.find("!3d") + 3
    end_index_lat = driver.current_url.find("!4d")
    lat = driver.current_url[start_index_lat:end_index_lat]
    start_index_long = driver.current_url.find("!4d") + 3
    end_index_long = driver.current_url.find("!", driver.current_url.find("!4d") + 1)
    long = driver.current_url[start_index_long:end_index_long]
    
    descriptionStr = address[0].text

    district = 0
    subDirstrict = 0

    print("LOCATION: " + lat + " " + long)
    if(len(description)):
        print("Description :",description[0].text)

    if(len(address)):
        useData = None
        for div in address:
            if provice in div.text and div.text.find(subStrDistict) != -1:
                useData = div.text.replace(",","").replace("เเ","แ")
        
        if(useData != None):
            print("Full Address :",useData)
            start_address_index = useData.find(subStrSubDistict)
            subAddress = useData[start_address_index:len(useData)]
            district = subAddress[subAddress.find(subStrDistict)+len(subStrDistict):subAddress.find(provice)].replace(" ","")
            subdistrict = subAddress[subAddress.find(subStrSubDistict)+len(subStrSubDistict):subAddress.find(subStrDistict)].replace(" ","")

            if district == "เมือง":
                district = district+provice

            filtered_rows = df[(df[1] == provice)&(df[4] == district)&(df[7] == subdistrict)]
            if not filtered_rows.empty:
                print("Provice :",filtered_rows.iloc[0, 0],provice)
                print("District :",filtered_rows.iloc[0, 3],district)
                print("SubDistrict :",filtered_rows.iloc[0, 6],subdistrict)
            else:
                print("Provice :",provice)
                print("District :",district)
                print("SubDistrict :",subdistrict)

        #openingDay = soup.find_all('td', class_='ylH6lf')
        #openingHour = soup.find_all('td', class_='mxowUb')
        score_div = soup.find_all('span', class_='ceNzKf')
        if len(score_div):
            score = score_div[0].get('aria-label').replace(" ","").replace("ดาว","")
            print("Rating score :",score)
            review_count = soup.find('span', {'aria-label': lambda x: x and 'รีวิว' in x}).text
            print("Rating Count:", review_count)

        ticketRating = soup.find_all('div', class_='drwWxc')
        if(len(ticketRating)):
            print("Ticket Price :",ticketRating[0].text)

        divContact = soup.find_all('div', class_='Io6YTe fontBodyMedium kR99db')
        
        for div in divContact:
            if(re.match(patternPhone,div.text) or re.match(patternPhoneService,div.text)):
                print("Contact :",div.text)
                break

        openingHourCheck = soup.find_all("span", class_="HlvSq")

        if(len(openingHourCheck) and openingHourCheck[0].text == "ดูเวลาทำการเพิ่มเติม"):
            infoOpening = driver.find_elements(By.CLASS_NAME, "HlvSq")
            for element in infoOpening:
                element.click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'y0skZc')))
            soup = BeautifulSoup(driver.page_source, 'html.parser')

        openingTime = soup.find_all("tr", class_="y0skZc")

        count = 0

        for data in openingTime:
            dateDiv = data.find("td", class_="ylH6lf")
            timeDiv = data.find("td", class_="mxowUb")
            print(dateDiv.text,timeDiv.text)
            count += 1
            if count == 7:
                break
        
        


    print("---------------------------")

while(True):
    pass

