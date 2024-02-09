from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
import requests


edge_driver_path = "D:\XSectorZ\GitHubRepoes\CEPPTravelScraping\CEPPWebScraping\msedgedriver.exe"
service = Service(executable_path=edge_driver_path)
driver = webdriver.Edge(service = service)
url = "https://thai.tourismthailand.org/Search-result/attraction?destination_id=238&sort_by=datetime_updated_desc&page=1&perpage=15&menu=attraction"
driver.get(url)
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'wrap-default-cards-articles')))
soup = BeautifulSoup(driver.page_source, 'html.parser')
card_elements = soup.find_all('div', class_='wrap-default-cards-articles')

for card in card_elements:
    attraction_name = card.find('div', class_='card-title').text.strip()
    print(attraction_name)

while(True):
    pass
