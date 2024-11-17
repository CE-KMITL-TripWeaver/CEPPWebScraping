from bs4 import BeautifulSoup
from selenium import webdriver
import pyautogui
import re
from bs4 import BeautifulSoup
import sys
sys.path.append('.')
import constants.constants as const
import constants.file_handler_constants as fh
from constants.attraction_constants import *

from packages.attraction.Attraction import *
from packages.file_handler_package.file_handler import *

import os
import glob
import time
import pandas as pd
import numpy as np
from dotenv import load_dotenv, dotenv_values 

from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver import ActionChains

from seleniumwire import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options


from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import requests
import google.generativeai as genai
from google.generativeai.types import ContentType
from PIL import Image
from IPython.display import Markdown

# for testing method implement multiprocessing in jupyternotebook
def test_mulProcess_method(num1):
    print("prn enter testMulProces")
    return 4 * num1

# for testing method implement multiprocessing in jupyternotebook
def test_mulProcess_more_params_method(num_1, num_2):
    print("prn enter testMulProces")
    return 4 * num_1 + num_2

def create_attraction_df(attraction: Attraction) -> pd.DataFrame:
    attraction_dict = {
        'name' : [attraction.get_name()],
        'type' : [attraction.get_type()],
        'description' : [attraction.get_description()],
        'latitude' : [attraction.get_latitude()],
        'longitude' : [attraction.get_longitude()],
        'imgPath' : [attraction.get_imgPath()],
        'phone': [attraction.get_phone()],
        'website': [attraction.get_website()],
        'openingHour': [attraction.get_openingHour()],

        # location
        'address' : [attraction.get_location().get_address()],
        'province' : [attraction.get_location().get_province()],
        'district' : [attraction.get_location().get_district()],
        'subDistrict' : [attraction.get_location().get_sub_district()],
        'province_code' : [attraction.get_location().get_province_code()],
        'district_code' : [attraction.get_location().get_district_code()],
        'sub_district_code' : [attraction.get_location().get_sub_district_code()],

        # rating
        'score' : [attraction.get_rating().get_score()],
        'ratingCount' : [attraction.get_rating().get_ratingCount()],
    }

    for cur_tag in ATTRACTION_TAG_SCORE:
        attraction_dict[cur_tag] = attraction.get_attractionTag().get_tag_score(cur_tag)

    attraction_df = pd.DataFrame(attraction_dict)
    
    return attraction_df.copy()


def convert_url_by_page(link_to_attraction: str, page: int) -> str:

    if(page == 1):
        return link_to_attraction
    
    first_page_url_split = link_to_attraction.split('-')
    nth_count_page = 'oa%s' % ((page - 1) * 30)
    first_page_url_split[-2] = nth_count_page
    res_page_url =  "-".join(first_page_url_split)

    return res_page_url


def extract_type_from_url(url: str) -> str:
    all_params_containers_str = url.split('/')[-1].split('&')
    
    if(len(all_params_containers_str) == 1):
        return ''
    
    for cur_container_str in all_params_containers_str:
        params, val = cur_container_str.split('=')
        if(params == 'type'):
            return val
        

def getScorefromGeminiAPI(name:str, latitude:float, longitude:float, all_img_url:list[str]) -> dict:
    """
    Gets tag scores for a given attraction using the Gemini API.

    Args:
        name: Name of the attraction.
        latitude: Latitude of the attraction.
        longitude: Longitude of the attraction.
        all_img_url: List of image URLs of the attraction.

    Returns:
        Dictionary representing scores for all tags.
    """

    # create a 'temp' directory to store temporarily downloaded images, which will be used in requests to the Gemini API
    createDirectory(fh.STORE_ATTRACTION_SCRAPING, 'temp')

    for Idx, cur_url in enumerate(all_img_url):
        if(cur_url == ''):
            break
        response = requests.get(cur_url)
        if response.status_code == 200:
            filename = 'temp/temp_img_{0}.jpeg'.format(Idx)
            with open(filename, 'wb') as file:
                file.write(response.content)

    # send API request to retrieve the score for the current attraction (including a query and the main image).
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    
    text_prompt = "Provide place name, latitude, and longitude. I will return a JSON string containing scores (0-1) for following attributes(nothing else no other sentences)" + \
    "\nfor example: \'{\"Tourism\":0,\"Adventure\":0,\"Meditation\":0,\"Art\":0,\"Cultural\":0,\"Landscape\":0,\"Nature\":0,\"Historical\":0,\"Cityscape\":0,\"Beach\":0,\"Mountain\":0,\"Architecture\":0,\"Temple\":0,\"WalkingStreet\":0,\"Market\":0,\"Village\":0,\"NationalPark\":0,\"Diving\":0,\"Snuggle\":0,\"Waterfall\":0,\"Island\":0,\"Shopping\":0,\"Camping\":0,\"Fog\":0,\"Cycling\":0,\"Monument\":0,\"Zoo\":0,\"Waterpark\":0,\"Hiking\":0,\"Museum\":0,\"Riverside\":0,\"NightLife\":0,\"Family\":0,\"Kid\":0,\"Landmark\":0,\"Forest\":0}" + \
    "\n{0}, {1}, {2} give me score for this".format(name, latitude, longitude)

    # send a prompt to the model
    prompt = [text_prompt]
    for Idx, cur_path_img in enumerate(glob.glob(os.path.join(fh.STORE_ATTRACTION_SCRAPING, 'temp', '*.jpeg'))):
        # use a maximum of 3 images in the prompt to reduce token usage.
        if(Idx == 3):
            break
        cur_img_prompt = Image.open(cur_path_img)
        prompt.append(cur_img_prompt)
        
    print("total_tokens: ", model.count_tokens(prompt))
    
    res_score_dict = {}
    try:
        response = model.generate_content(prompt)
        # remove directory 'temp'
        removeNoneEmptyDir(os.path.join(fh.STORE_ATTRACTION_SCRAPING, 'temp'))
        res_start_Idx = response.text.find('{')
        res_end_Idx = response.text.find('}')
        res_score_dict =  json.loads(response.text[res_start_Idx:res_end_Idx+1])

    except Exception as e:
        # remove directory 'temp'
        removeNoneEmptyDir(os.path.join(fh.STORE_ATTRACTION_SCRAPING, 'temp'))
        print("failed to use gemini api")
    
    return res_score_dict


def scrape_img(attraction_page_driver: webdriver) -> list[str]:

    res_imgPath = []

    possible_click_img_xpath = [
        '//*[@id="AR_ABOUT"]/div[2]/div/div/div/div/div[1]/div/div[3]/button',
        '//*[@id="AR_ABOUT"]/div[2]/div/div/div/div/div[1]/div/div/div/div[1]/div/div[7]/button',
        '//*[@id="AR_ABOUT"]/div/div/div/div/div/div[1]/div/div/div/div[1]/div/div[7]/button',
    ]
    
    btn_img_xpath = ""
    print('y2')
    for cur_xpath in possible_click_img_xpath:
        try:
            WebDriverWait(attraction_page_driver, 2).until(EC.visibility_of_element_located((By.XPATH, cur_xpath)))
            btn_img_xpath = cur_xpath
            break
        
        except Exception as e:
            pass
    
    if(not len(btn_img_xpath)):
        print("can't scrape img (no img ?)")
        return ['']

    # find button and click
    # to see modal then scrape image address
    try:
        # WebDriverWait(attraction_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, btn_img_xpath)))
        print('y3')
        click_img_btn = attraction_page_driver.find_element(By.XPATH, btn_img_xpath)

        # Move to the element and click
        print("y4")
        actions = ActionChains(attraction_page_driver)
        actions.move_to_element(click_img_btn).click().perform()
        print("y5")
        
        print("cur img url --> ", attraction_page_driver.current_url)

        type_value = extract_type_from_url(url=attraction_page_driver.current_url)
        print("cur img section type --> ", type_value)

        
        # case 1 img section UI:  https://th.tripadvisor.com/Attraction_Review-g297930-d1866109-Reviews-Bangla_Road-Patong_Kathu_Phuket.html#/media/1866109/?albumid=-160&type=ALL_INCLUDING_RESTRICTED&category=-160
        if(type_value == "ALL_INCLUDING_RESTRICTED"):
            print("enter case 1 img ...")
            is_end_scrape_img = False
            cnt_retry = 0
            while(not is_end_scrape_img):
                if(cnt_retry == 10):
                    print("max retry for scrape image...")
                    break
                
                try:
                    WebDriverWait(attraction_page_driver, 2).until(EC.visibility_of_element_located((By.CLASS_NAME, 'BtGfv')))
                    all_img_containers = attraction_page_driver.find_elements(By.CLASS_NAME, 'BtGfv')
                    print("find image element -> ", len(all_img_containers))
                    for cur_container in all_img_containers:
                        cur_img_element = cur_container.find_element(By.TAG_NAME, 'img')
                        cur_bgImg_val = cur_img_element.get_attribute('src')
                        res_imgPath.append(cur_bgImg_val)
                        
                    is_end_scrape_img = True

                except Exception as e:
                    cnt_retry += 1
                    print("retry scrape img case 1 ...")


        # case 2 img section UI: https://th.tripadvisor.com/Attraction_Review-g297930-d1866109-Reviews-Bangla_Road-Patong_Kathu_Phuket.html#/media-atf/1866109/?albumid=-160&type=0&category=-160
        else:
            print("enter case 2 img ...")
            is_end_scrape_img = False
            cnt_retry = 0
            while(not is_end_scrape_img):
                if(cnt_retry == 10):
                    print("max retry for scrape image...")
                    break
                
                try:
                    WebDriverWait(attraction_page_driver, 2).until(EC.visibility_of_element_located((By.CLASS_NAME, 'cfCAA')))
                    all_img_elements = attraction_page_driver.find_elements(By.CLASS_NAME, 'cfCAA')
                    print("find image element -> ", len(all_img_elements))
                    for cur_img_element in all_img_elements:
                        cur_bgImg_val = cur_img_element.value_of_css_property('background-image')
                        match = re.search(r'url\("(.*?)"\)', cur_bgImg_val)
                        if match:
                            res_imgPath.append(match.group(1))

                    is_end_scrape_img = True

                except Exception as e:
                    cnt_retry += 1
                    print("retry scrape img case 2 ...")
        
    except Exception as e:
        print("can't scrape img ")
    

    return res_imgPath.copy()


def scrape_location(attraction_page_driver: webdriver, latitude: float, longitude: float, province_th: str) -> Location:

    # find better address description on wongnai
    # for example: "991 ถนนพระราม 1 Pathum Wan, กรุงเทพมหานคร (กทม.) 10330 ไทย"
    address_tripAdvisor = ""
    possible_address_xpath = [
        '//*[@id="tab-data-WebPresentation_PoiLocationSectionGroup"]/div/div/div[2]/div[1]/div/div/div/div[1]/button/span',
        '//*[@id="tab-data-WebPresentation_PoiLocationSectionGroup"]/div/div/div[2]/div[1]/div/div/div/div/button/span',
        '//*[@id="tab-data-WebPresentation_PoiLocationSectionGroup"]/div/div/div[2]/div[1]/div/div/div/div[1]/button/span'
    ]


    for cur_address_xpath in possible_address_xpath:
        try:
            WebDriverWait(attraction_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, cur_address_xpath)))
            address_element = attraction_page_driver.find_element(By.XPATH, cur_address_xpath)
            address_tripAdvisor = address_element.text
            
        except Exception as e:
            pass


    # start scrape location
    res_location = Location()
    cnt_retry = 0
    try:
        while(True):
            if(cnt_retry == 10):
                print("max retry for scrape Google Map ...")
                break
            
            # set up new webdriver to work googlemap url(query for specific lat/long)
            possible_addressGoogleMap_elements = []
            try:
                # set Chrome options to run in headless mode
                # options = Options()
                options = webdriver.ChromeOptions()
                options.add_argument("start-maximized")
                # options.add_argument("--headless=new")
                options.add_experimental_option(
                    "prefs", {"profile.managed_default_content_settings.images": 2}
                )

                google_map_driver = webdriver.Chrome(options=options)
                
                google_map_query = "https://www.google.com/maps/search/?api=1&query=%s,%s" % (latitude, longitude)
                google_map_driver.get(google_map_query)
                print("scrape location data for, ", google_map_query)
                
                WebDriverWait(google_map_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'DkEaL')))
                possible_addressGoogleMap_elements = google_map_driver.find_elements(By.CLASS_NAME, 'DkEaL')

            except Exception as e:
                print("retry  scrape Google Map..")
                cnt_retry += 1
                google_map_driver.close()
                continue


            # after init new webdriver -> continure scrape location data

            # if found some wiered place that doesn't even have its address
            # skip this case for now...
            if(not len(possible_addressGoogleMap_elements)):
                return res_location

            subStrDistrict = "อำเภอ"
            subStrSubDistrict = "ตำบล"

            if province_th == "กรุงเทพมหานคร":
                subStrDistrict = "เขต"
                subStrSubDistrict = "แขวง"

            district = 0
            subDirstrict = 0

            # find location
            useData = None
            for cur_element in possible_addressGoogleMap_elements:
                if province_th in cur_element.text and cur_element.text.find(subStrDistrict) != -1:
                    useData = cur_element.text.replace(",","").replace("เเ","แ")
                    break
           
            if(useData != None):
                # print("Full Address :",useData)
                # another brute force way in case of province 'กรุงเทพหมานคร' not have word 'แขวง' in address
                if(province_th == 'กรุงเทพมหานคร' and useData.find(subStrSubDistrict) == -1):
                    subAddress_split = useData.split(' ')
                    cur_province_Idx = subAddress_split.index(province_th)
                    district = subAddress_split[cur_province_Idx - 1].replace("เขต","")

                else:
                    start_address_index = useData.find(subStrDistrict)
                    subAddress = useData[start_address_index:]
                    district = subAddress[subAddress.find(subStrDistrict)+len(subStrDistrict):subAddress.find(province_th)].replace(" ","")               

                if district == "เมือง":
                    district = district+province_th

                # filter row to find 'ISO_3166_code', 'zip_code', 'geo_code'
                geo_code_df = pd.read_csv(fh.PATH_TO_GEOCODE)
                filtered_rows = geo_code_df[
                    (geo_code_df['province_th'] == province_th) & (geo_code_df['district_th'] == district)
                ]
                filtered_rows.reset_index(inplace=True, drop=True)
                
                if not filtered_rows.empty:
                    print("found province :",filtered_rows.loc[0, 'ISO_3166_code'], province_th)
                    print("found District :",filtered_rows.loc[0, 'zip_code'], district)

                    res_location.set_address(address_tripAdvisor if len(address_tripAdvisor) else useData)
                    res_location.set_province(province_th)
                    res_location.set_district(district)
                    res_location.set_sub_district("")
                    res_location.set_province_code(filtered_rows.loc[0, 'ISO_3166_code'])
                    res_location.set_district_code(filtered_rows.loc[0, 'zip_code'])
                    res_location.set_sub_district_code(0)

                else:
                    print("not found province :", province_th)
                    print("not found District :", district)

                    res_location.set_address(address_tripAdvisor if len(address_tripAdvisor) else useData)
                    res_location.set_province(province_th)
                    res_location.set_district(district)
                    res_location.set_sub_district("")
                    res_location.set_province_code(0)
                    res_location.set_district_code(0)
                    res_location.set_sub_district_code(0)

            google_map_driver.close()
            break

    except Exception as e:
        print("can't scrape location data")

    return res_location


# scrape lat/long, openingHours, types (there are in another page of current attraction)
def scrape_adjust_page(link_to_adjust_page: str) -> tuple[float, float, dict, list[str]]:
    lat = 0
    long = 0
    openingHours = {}
    types = []

    # create new webdriver to continue scrape lat/long, openingHours in adjust attraction page
    cnt_retry = 0
    
    while(True):
        # if(cnt_retry == 10):
        #     print("max retry for scrape single attraction ...")
        #     break

        # formulate the proxy url with authentication
        proxy_url = f"http://{os.environ['proxy_username']}:{os.environ['proxy_password']}@{os.environ['proxy_address']}:{os.environ['proxy_port']}"
        
        # set selenium-wire options to use the proxy
        seleniumwire_options = {
            "proxy": {
                "http": proxy_url,
                "https": proxy_url
            },
        }

        # set Chrome options to run in headless mode
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--lang=th-TH")
        # options.add_argument("--headless=new")
        options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )

        # initialize the Chrome driver with service, selenium-wire options, and chrome options
        adjust_page_driver = webdriver.Edge(
            service=Service(EdgeChromiumDriverManager().install()),
            seleniumwire_options=seleniumwire_options,
            options=options
        )
        
        # retry in case of web restrictions, some elements not loaded
        try:
            print("scrape data in adjust attraction page...")
            print("for link : ", link_to_adjust_page)
            adjust_page_driver.get(link_to_adjust_page)

            print("debug option of adjust page: ")
            WebDriverWait(adjust_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'DiHOR')))

            # find dropdown --> click display data below --> cick display lat/long input form
            possible_target_btn = adjust_page_driver.find_elements(By.CLASS_NAME, 'DiHOR')
            for cur_dropdown_btn in possible_target_btn:
                cur_dropdown_text = cur_dropdown_btn.text
                if("แนะนำการแก้ไขข้อมูลของสถานที่นี้" in cur_dropdown_text):
                    print("found target dropdown btn ...")
                    cur_dropdown_btn.click()
                    WebDriverWait(adjust_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lithium-root"]/main/div[2]/div[3]/div[1]/div/div[2]/div[2]/div/div/div[2]/button')))
                    # find button click to display lat/long input form
                    display_lat_long_btn = adjust_page_driver.find_element(By.XPATH, '//*[@id="lithium-root"]/main/div[2]/div[3]/div[1]/div/div[2]/div[2]/div/div/div[2]/button')
                    display_lat_long_btn.click()

        except Exception as e:
            cnt_retry += 1
            adjust_page_driver.quit()
            print("retry adjust page...")
            continue

      
        # find lat/long
        try:
            WebDriverWait(adjust_page_driver, 2).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lithium-root"]/main/div[2]/div[3]/div[1]/div/div[2]/div[2]/div/div/div[2]/div/div/div[3]/div[1]/div/div[2]/div/div/div/span')))
            WebDriverWait(adjust_page_driver, 2).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lithium-root"]/main/div[2]/div[3]/div[1]/div/div[2]/div[2]/div/div/div[2]/div/div/div[3]/div[2]/div/div[2]/div/div/div/span')))
    
            lat_input_container = adjust_page_driver.find_element(By.XPATH, '//*[@id="lithium-root"]/main/div[2]/div[3]/div[1]/div/div[2]/div[2]/div/div/div[2]/div/div/div[3]/div[1]/div/div[2]/div/div/div/span')
            lat_input_element = lat_input_container.find_element(By.TAG_NAME, 'input')
            lat = float(lat_input_element.get_attribute('value'))

            long_input_container = adjust_page_driver.find_element(By.XPATH, '//*[@id="lithium-root"]/main/div[2]/div[3]/div[1]/div/div[2]/div[2]/div/div/div[2]/div/div/div[3]/div[2]/div/div[2]/div/div/div/span')
            long_input_element = long_input_container.find_element(By.TAG_NAME, 'input')
            long = float(long_input_element.get_attribute('value'))

        except Exception as e:
            print("can't find lat/long")
        
        print("lat : ", lat)
        print("long : ", long)

        # **if can't find lat/long --> don't scrape this attaction
        if(lat == 0 and long == 0):
            print("in scrape_adjust_page --> can't find lat/long --> 0, 0")
            return lat, long, openingHours.copy(), types.copy()


        # find openingHours
        try:
            WebDriverWait(adjust_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'dNAjp')))
            all_openingHours_container = adjust_page_driver.find_elements(By.CLASS_NAME, 'dNAjp')
            for cur_openingHours_container in all_openingHours_container:
                cur_day_element = cur_openingHours_container.find_element(By.CLASS_NAME, 'ngXxk')
                cur_day_text = cur_day_element.text.replace(":", "")

                cur_time_element = cur_openingHours_container.find_element(By.CLASS_NAME, 'KxBGd')
                cur_time_text = cur_time_element.text

                openingHours[cur_day_text] = cur_time_text

        except Exception as e:
            print("can't find openingHours ...")

        print("openingHours : ", openingHours.copy())


        # find types
        try:
            WebDriverWait(adjust_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'ZCWaz')))
            all_type_elements = adjust_page_driver.find_elements(By.CLASS_NAME, 'ZCWaz')
            for cur_element in all_type_elements:
                cur_type_text = cur_element.text
                types.append(cur_type_text)

        except Exception as e:
            print("can't find types ...")

        print("types : ", types.copy())
        

        adjust_page_driver.quit()
        break

    return lat, long, openingHours.copy(), types.copy()


def scrape_single_attraction(link_to_attraction: str, province_th: str) -> Attraction:
    
    attraction = Attraction()
    cnt_retry = 0
    
    while(True):
        if(cnt_retry == 10):
            print("max retry for scrape single attraction ...")
            break

        # formulate the proxy url with authentication
        proxy_url = f"http://{os.environ['proxy_username']}:{os.environ['proxy_password']}@{os.environ['proxy_address']}:{os.environ['proxy_port']}"
        
        # set selenium-wire options to use the proxy
        seleniumwire_options = {
            "proxy": {
                "http": proxy_url,
                "https": proxy_url
            },
        }

        # set web browser options to run
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--lang=th-TH")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36")
        options.add_experimental_option(
            "prefs", 
            {
                "profile.managed_default_content_settings.images": 2, # Disable image
                "profile.default_content_setting_values.cookies": 2,  # Block all cookies
                "profile.default_content_settings.popups": 0,         # Disable popups
                "profile.managed_default_content_settings.cookies": 2  # Disable third-party cookies
            }
        )

        # initialize the web driver with service, selenium-wire options, and web browser options
        attraction_page_driver = webdriver.Edge(
            service=Service(EdgeChromiumDriverManager().install()),
            seleniumwire_options=seleniumwire_options,
            options=options
        )
        
        # retry in case of web restrictions and some elements not loaded
        try:
            print("******************************************************")
            print("scrape single attraction...")
            print("for attraction : ", link_to_attraction)
            # attraction_page_driver.get(link_to_attraction)
            attraction_page_driver.get('https://th.tripadvisor.com/Attraction_Review-g1389361-d2433844-Reviews-Big_Buddha_Phuket-Chalong_Phuket_Town_Phuket.html')

            print("debug scrape_single_attraction: common component section")
            WebDriverWait(attraction_page_driver, 2).until(EC.visibility_of_element_located((By.CLASS_NAME, 'IDaDx')))
            
        except Exception as e:
            print("retry single attraction case 1...")
            cnt_retry += 1
            attraction_page_driver.quit()
            continue
        
        # convert attraction url to adjust page url
        # for example: from 'https://th.tripadvisor.com/Attraction_Review-g297930-d1866109-Reviews-Bangla_Road-Patong_Kathu_Phuket.html' to 'https://th.tripadvisor.com/ImproveListing-d1866109.html'
        link_to_adjust_page = 'https://th.tripadvisor.com/ImproveListing-%s.html' % (link_to_attraction.split('-')[2])

        # ** find lat/long, openingHours, types (there are in another page of current attraction)
        # ** if this attraction not have lat/long
        # ** don't continue to scrape
        lat, long, openingHours, types = scrape_adjust_page(
            link_to_adjust_page = link_to_adjust_page
        )
        
        # **if can't find lat/long --> don't scrape this attaction
        if(lat == 0 and long == 0):
            print("in scrape_single_attraction --> can't find lat/long --> don't scrape this attraction ...")
            attraction_page_driver.quit()
            return attraction

        # find name
        name = ""
        try:
            WebDriverWait(attraction_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lithium-root"]/main/div[1]/div[2]/div[1]/header/div[3]/div[1]/div/h1')))
            name_element = attraction_page_driver.find_element(By.XPATH, '//*[@id="lithium-root"]/main/div[1]/div[2]/div[1]/header/div[3]/div[1]/div/h1')
            name = name_element.text

        except Exception as e:
            print("can't find name")

        print("name -> ", name)

        # find description
        description = ""
        try:
            WebDriverWait(attraction_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="AR_ABOUT"]/div[1]')))
            
            description_container = attraction_page_driver.find_element(By.XPATH, '//*[@id="AR_ABOUT"]/div[1]')
            header_element = description_container.find_element(By.CLASS_NAME, 'biGQs')
            header_text = header_element.text
            if(header_text == 'ข้อมูล'):
                description_element = attraction_page_driver.find_element(By.CLASS_NAME, 'JguWG')
                description = description_element.text
                

        except Exception as e:
            print("can't find description")

        print("description -> ", description)
        
        # find rating
        rating = 0
        rating_count = 0
        try:
            WebDriverWait(attraction_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lithium-root"]/main/div[1]/div[2]/div[2]/div[2]/div/div[1]/section[1]/div/div/div/div/div[1]/div[1]/a/div')))
            score_element = attraction_page_driver.find_element(By.XPATH, '//*[@id="lithium-root"]/main/div[1]/div[2]/div[2]/div[2]/div/div[1]/section[1]/div/div/div/div/div[1]/div[1]/a/div')
            score_text_list = score_element.get_attribute('aria-label').split(' ')
            for Idx in range(1, len(score_text_list)):
                # set rating
                if(score_text_list[Idx - 1] == "คะแนน"):
                    rating = float(score_text_list[Idx])

                elif(score_text_list[Idx - 1] == "รีวิว"):
                    rating_count = int(score_text_list[Idx].replace(',', ''))

        except Exception as e:
            print("can't find rating and rating_count")

        print("rating --> ", rating)
        print("rating_count --> ", rating_count)

        # find img_path
        img_path = scrape_img(attraction_page_driver)
        print("cur img path -> ", img_path)

        # find location
        location = scrape_location(
            attraction_page_driver = attraction_page_driver,
            latitude = lat,
            longitude = long,
            province_th = province_th
        )
        print("province :", location.get_province_code(), location.get_province())
        print("District :", location.get_district_code(), location.get_district())
        print("Address : ", location.get_address())

        # find attractionTag score
        # attractionTag_score = getScorefromGeminiAPI(
        #     name = name,
        #     latitude = lat,
        #     longitude = long,
        #     all_img_url = img_path
        # )
        # print("attractionTag score : ")
        # print(attractionTag_score)

        # set some of "Attraction" object properties
        attraction.set_name(name)
        attraction.set_type(types)
        attraction.set_description(description)
        attraction.set_latitude(lat)
        attraction.set_longitude(long)
        attraction.set_imgPath(img_path)
        attraction.set_website(link_to_attraction)
        attraction.set_openingHour(openingHours)
        attraction.set_location(
            address = location.get_address(),
            province = location.get_province(),
            district = location.get_district(),
            sub_district = location.get_sub_district(),
            province_code = location.get_province_code(),
            district_code = location.get_district_code(),
            sub_district_code = location.get_sub_district_code()
        )
        attraction.set_rating(
            score = rating,
            rating_count = rating_count
        )
        # attraction.set_attractionTag(attractionTag_score)

        attraction_page_driver.quit()
        break

    return attraction


def get_all_url_by_page(query_url: str, page: int) -> list[str]:

    res_url_by_page = []

    cnt_retry = 0
    
    while(True):
        
        if(cnt_retry == 10):
            print("max retry for scrape data by page ...")
            break

        # formulate the proxy url with authentication
        # os.environ['proxy_port']
        proxy_url = f"http://{os.environ['proxy_username']}:{os.environ['proxy_password']}@{os.environ['proxy_address']}:{os.environ['proxy_port']}"
        
        # set selenium-wire options to use the proxy
        seleniumwire_options = {
            "proxy": {
                "http": proxy_url,
                "https": proxy_url
            },
        }

        # set Chrome options to run in headless mode
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--lang=th-TH")
        # options.add_argument("--headless=new")
        options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )
      
        # initialize the Chrome driver with service, selenium-wire options, and chrome options
        driver = webdriver.Edge(
            service=Service(EdgeChromiumDriverManager().install()),
            seleniumwire_options=seleniumwire_options,
            options=options
        )
        
        # just check for ip
        # print("just check for ip :")
        # driver.get("https://httpbin.io/ip")
        # print(driver.page_source)

        # find group of attraction on the nth page
        all_attractions_card = []

        # retry in case of web restrictions and some elements not loaded
        try:
            query_url_by_page = convert_url_by_page(
                link_to_attraction = query_url,
                page = page
            )
            driver.get(query_url_by_page)
            # scroll and wait for some msec
            driver.execute_script('window.scrollBy(0, document.body.scrollHeight)')
            
            print("check current page url --> ", driver.current_url)

            # wait for div (each attraction section) to be present and visible
            print("b1")
            print("debug get_all_url_by_page: attraction by one page section")
            # WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'XJlaI')))
            WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'KRObB')))

            print("b2")
            print("debug get_all_url_by_page: text")
            # WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'BKifx')))
            WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'sVTRu')))

            # print("b3")
            # print("debug get_all_url_by_page: link to single attraction")
            # WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.TAG_NAME, 'a')))

            print("b3")
            print("check in loop ...")
            # all_attractions_card = driver.find_elements(By.CLASS_NAME, 'XJlaI')
            all_attractions_card = driver.find_elements(By.CLASS_NAME, 'KRObB')
            for cur_attraction_card in all_attractions_card:
    
                cur_attraction_url = cur_attraction_card.find_element(By.TAG_NAME, 'a').get_attribute('href')

                # check_text = cur_attraction_card.find_element(By.CLASS_NAME, 'BKifx').text  
                check_text = cur_attraction_card.find_element(By.CLASS_NAME, 'sVTRu').text  
               
                # check if cuurent card is for attraction ?
                is_attraction_keyword = True
                not_attraction_keyword = ['ทัวร์', 'ทริป', "สปา", "กิจกรรมทางวัฒนธรรม", 'ชั้นเรียน', 'รถรับส่ง', 'อุปกรณ์ให้เช่า', 'ร้านขายของ', 'นั่งเรือเที่ยว']
                for cur_check_word in not_attraction_keyword:
                    if(cur_check_word in check_text):
                        is_attraction_keyword = False
                        break
                
                if(is_attraction_keyword):
                    print("cur_attraction_url : ", cur_attraction_url)
                    print("check cur text : ", check_text)
                    res_url_by_page.append(cur_attraction_url)
            
            driver.quit()
            break
            
        except Exception as e:
            print("retry find get_all_url_by_page ...")
            cnt_retry += 1
            driver.quit()
            continue

    return res_url_by_page.copy()


def mulProcess_helper_scrape_attraction_by_province(page: int, province_url: str, province: str) -> pd.DataFrame:
    # res_attraction_df = pd.DataFrame()
    res_attraction_df = create_attraction_df(Attraction())
    
    cnt_for_debug = 0
        
    print("scraping attraction | province --> %s | page --> %s" % (province, page))

    all_url_by_page = get_all_url_by_page(query_url = province_url, page = page)

    # use data from 'res_get_data_by_page' to retrive data of specific attraction
    for cur_attraction_url in all_url_by_page:
        if(cnt_for_debug == 3):
            break

        # continue scraping data for a specific resgtaurant
        cur_attraction = scrape_single_attraction(
            link_to_attraction = cur_attraction_url,
            province_th = province
        )
        cnt_for_debug += 1


        # create data frame represent data scrape from current attraction card
        cur_attraction_df = create_attraction_df(attraction=cur_attraction)

        # concat all data frame result
        res_attraction_df = pd.concat([res_attraction_df, cur_attraction_df])
    
    return res_attraction_df.iloc[1:, :].copy()


