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


edge_driver_path = "D:\XSectorZ\GitHubRepoes\CEPPTravelScraping\CEPPWebScraping\msedgedriver.exe"
service = Service(executable_path=edge_driver_path)
driver = webdriver.Edge(service = service)
#url = "https://thai.tourismthailand.org/Search-result/attraction?destination_id=238&sort_by=datetime_updated_desc&page=1&perpage=15&menu=attraction"
url = "https://www.google.com/maps/search/%E0%B8%AA%E0%B8%96%E0%B8%B2%E0%B8%99%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%97%E0%B9%88%E0%B8%AD%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%A7%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/@13.5524175,98.9526212,9z/data=!3m1!4b1?entry=ttu"
driver.get(url)
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'hfpxzc')))
list_card = driver.find_elements(By.CLASS_NAME, "hfpxzc")
action = ActionChains(driver)
max_length = 0

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
    time.sleep(3)
    print(name[0].text)
    start_index_lat = driver.current_url.find("!3d") + 3
    end_index_lat = driver.current_url.find("!4d")
    lat = driver.current_url[start_index_lat:end_index_lat]
    start_index_long = driver.current_url.find("!4d") + 3
    end_index_long = driver.current_url.find("!15s")
    long = driver.current_url[start_index_long:end_index_long]
    
    print("LOCATION: " + lat + " " + long)
    print("---------------------------")
#soup = BeautifulSoup(driver.page_source, 'html.parser')
#card_elements = soup.find_all('div', class_='wrap-default-cards-articles')

#for card in card_elements:
#    attraction_name = card.find('div', class_='card-title').text.strip()
#    print(attraction_name)

while(True):
    pass

