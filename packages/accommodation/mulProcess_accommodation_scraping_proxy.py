from bs4 import BeautifulSoup
from selenium import webdriver
import pyautogui
import re
from bs4 import BeautifulSoup
import sys
sys.path.append('.')
import constants.constants as const
import constants.file_handler_constants as fh
from constants.accommodation_constants import *

from packages.accommodation.accommodation import *
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

# for testing method implement multiprocessing in jupyternotebook
def test_mulProcess_method(num1):
    print("prn enter testMulProces")
    return 4 * num1

# for testing method implement multiprocessing in jupyternotebook
def test_mulProcess_more_params_method(num_1, num_2):
    print("prn enter testMulProces")
    return 4 * num_1 + num_2

def create_accommodation_df(accommodation: Accommodation) -> pd.DataFrame:
    accommodation_dict = {
        'name' : [accommodation.get_name()],
        'description' : [accommodation.get_description()],
        'latitude' : [accommodation.get_latitude()],
        'longitude' : [accommodation.get_longitude()],
        'imgPath' : [accommodation.get_imgPath()],
        'phone': [accommodation.get_phone()],
        'website': [accommodation.get_website()],
        'star': [accommodation.get_star()],
        'facility': [accommodation.get_facility()],
        'tag': [accommodation.get_tag()],
        'type': [accommodation.get_type()],

        # location
        'address' : [accommodation.get_location().get_address()],
        'province' : [accommodation.get_location().get_province()],
        'district' : [accommodation.get_location().get_district()],
        'subDistrict' : [accommodation.get_location().get_sub_district()],
        'province_code' : [accommodation.get_location().get_province_code()],
        'district_code' : [accommodation.get_location().get_district_code()],
        'sub_district_code' : [accommodation.get_location().get_sub_district_code()],

        # rating
        'score' : [accommodation.get_rating().get_score()],
        'ratingCount' : [accommodation.get_rating().get_ratingCount()],
    }

    accommodation_df = pd.DataFrame(accommodation_dict)
    
    return accommodation_df.copy()


def convert_url_by_page(link_to_accommodation: str, page: int) -> str:

    if(page == 1):
        return link_to_accommodation
    
    first_page_url_split = link_to_accommodation.split('-')
    nth_count_page = 'oa%s' % ((page - 1) * 30)
    first_page_url_split[-2] = nth_count_page
    res_page_url =  "-".join(first_page_url_split)

    return res_page_url


def scrape_img(accommodation_page_driver: webdriver) -> list[str]:
    
    res_imgPath = []

    # find button and click
    # to see image modal
    try:
        print("p2")
        # click_img_btn = accommodation_page_driver.find_element(By.CLASS_NAME, 'QXsnf')
        click_img_btn = accommodation_page_driver.find_element(By.CLASS_NAME, 'GuzzA')
        print("p3")
        
        # Move to the element and click
        actions = ActionChains(accommodation_page_driver)
        actions.move_to_element(click_img_btn).click().perform()
        
    except Exception as e:
        print("can't open modal image")
        return res_imgPath

    # scrape image address
    try:
        is_end_scrape_img = False
        cnt_retry = 0
        print("p7")
        while(not is_end_scrape_img):
            if(cnt_retry == 20):
                print("max retry for scrape image...")
                break
            
            try:
                WebDriverWait(accommodation_page_driver, 2).until(EC.visibility_of_element_located((By.CLASS_NAME, 'cfCAA')))
                all_img_elements = accommodation_page_driver.find_elements(By.CLASS_NAME, 'cfCAA')
                print("find image element -> ", len(all_img_elements))
                for cur_img_element in all_img_elements:
                    cur_bgImg_val = cur_img_element.value_of_css_property('background-image')
                    match = re.search(r'url\("(.*?)"\)', cur_bgImg_val)
                    if match:
                        res_imgPath.append(match.group(1))

                is_end_scrape_img = True

            except Exception as e:
                cnt_retry += 1
                print("retry scrape img...")
        
    except Exception as e:
            pass
    

    return res_imgPath.copy()


def scrape_location(accommodation_page_driver: webdriver, latitude: float, longitude: float, province_th: str) -> Location:

    # find better address description on wongnai
    # for example: "991 ถนนพระราม 1 Pathum Wan, กรุงเทพมหานคร (กทม.) 10330 ไทย"
    address_tripAdvisor = ""
    possible_address_xpath = [
        '//*[@id="lithium-root"]/main/span/div[4]/div/div[1]/div[3]/div/div[3]/div[1]/div[2]/span[2]/span',
        '//*[@id="lithium-root"]/main/span/div[4]/div/div[1]/div[3]/div/div[3]/div[1]/div[1]/span[2]/span',
    ]


    for cur_address_xpath in possible_address_xpath:
        try:
            WebDriverWait(accommodation_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, cur_address_xpath)))
            address_element = accommodation_page_driver.find_element(By.XPATH, cur_address_xpath)
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


# scrape lat/long, and types (there are in another page of current accommodation)
def scrape_location_latlong_types(accommodation_page_driver: webdriver, link_to_adjust_page: str) -> tuple[float, float, list[str]]:
    lat = 0
    long = 0

    # create new webdriver to continue scrape lat/long, openingHours in adjust accommodation page
    cnt_retry = 0
    
    while(True):
        # if(cnt_retry == 10):
        #     print("max retry for scrape single accommodation ...")
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
            print("scrape data in adjust accommodation page...")
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
            print("in scrape_location_latlong_openingHours --> can't find lat/long --> 0, 0")
            return lat, long, ["ไม่รู้จัก"]

        # find type
        types = []
        all_accomodation_types = ["โรงแรม", "โมเตล", "รีสอร์ท", "ที่พักพร้อมอาหารเช้า", "โรงแรมขนาดเล็ก", "Condominium/Apartment", "วิลล่า", "พื้นที่ตั้งแคมป์", "โฮสเทล", "Vacation Rental House", "ไม่รู้จัก"] 
        try:
            # PMWyE
            WebDriverWait(adjust_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'PMWyE')))
            all_checkbox_containers = adjust_page_driver.find_elements(By.CLASS_NAME, 'PMWyE')
            for i in range(len(all_checkbox_containers)):
                cur_checkbox = all_checkbox_containers[i].find_element(By.TAG_NAME, 'span')
                is_check = True if cur_checkbox.get_attribute('class') != 'U' else False
                if(is_check):
                    types.append(all_accomodation_types[i])

        except Exception as e:
            print("can't find type")

        print("types --> ", types)

        adjust_page_driver.quit()
        break

    return lat, long, types.copy()


def scrape_single_accommodation(link_to_accommodation: str, province_th: str) -> Accommodation:
    
    accommodation = Accommodation()
    cnt_retry = 0
    
    while(True):
        # if(cnt_retry == 10):
        #     print("max retry for scrape single accommodation ...")
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
            "prefs", 
            {
                "profile.managed_default_content_settings.images": 2, # Disable image
                "profile.default_content_setting_values.cookies": 2,  # Block all cookies
                "profile.default_content_settings.popups": 0,         # Disable popups
                "profile.managed_default_content_settings.cookies": 2  # Disable third-party cookies
            }
        )

        # initialize the Chrome driver with service, selenium-wire options, and chrome options
        accommodation_page_driver = webdriver.Edge(
            service=Service(EdgeChromiumDriverManager().install()),
            seleniumwire_options=seleniumwire_options,
            options=options
        )
        
        # retry in case of web restrictions and some elements not loaded
        try:
            print("******************************************************")
            print("scrape single accommodation...")
            print("for accommodation : ", link_to_accommodation)
            accommodation_page_driver.get(link_to_accommodation)
            # accommodation_page_driver.add_cookie()

            print("debug scrape_single_accommodation: top info component section")
            # WebDriverWait(accommodation_page_driver, 2).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lithium-root"]/main/span/div[4]/div/div[1]/div[3]/div')))
            # top_info_container = accommodation_page_driver.find_element(By.XPATH, '//*[@id="lithium-root"]/main/span/div[4]/div/div[1]/div[3]/div')

            print("debug scrape_single_accommodation: bottom info component section")
            WebDriverWait(accommodation_page_driver, 2).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="ABOUT_TAB"]')))
            bottom_info_container = accommodation_page_driver.find_element(By.XPATH, '//*[@id="ABOUT_TAB"]')

            print("debug scrape_single_attraction: common component section")
            WebDriverWait(accommodation_page_driver, 2).until(EC.visibility_of_element_located((By.CLASS_NAME, 'IDaDx')))

        except Exception as e:
            print("retry single accommodation case 1...")
            cnt_retry += 1
            accommodation_page_driver.quit()
            continue
        


        # find name
        name = ""
        try:
            WebDriverWait(accommodation_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'rRtyp')))
            name_element = accommodation_page_driver.find_element(By.CLASS_NAME, 'rRtyp')
            name = name_element.text

        except Exception as e:
            print("can't find name")

        print("name -> ", name)

        # find description
        description = ""
        try:
            try:
                # find button to click readmore (if it exists, it likely to be the first elements of class 'lszDU')
                WebDriverWait(accommodation_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lszDU')))
                click_readmore_btn = accommodation_page_driver.find_element(By.CLASS_NAME, 'lszDU')
                click_readmore_btn.click()

            except Exception as e:
                pass

            WebDriverWait(accommodation_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'zYHGB')))
            all_description_elements = accommodation_page_driver.find_elements(By.CLASS_NAME, 'zYHGB')
            for cur_element in all_description_elements:
                cur_text =  cur_element.text
                if(len(cur_text)):
                    description += cur_text + '\n'
            
        except Exception as e:
            print("can't find description")

        print("description -> ", description)
        
        # find phone
        phone = ""
        try:
            WebDriverWait(accommodation_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lithium-root"]/main/span/div[4]/div/div[1]/div[3]/div/div[3]/div[1]/div[3]/div[2]/div/a')))
            phone_element = accommodation_page_driver.find_element(By.XPATH, '//*[@id="lithium-root"]/main/span/div[4]/div/div[1]/div[3]/div/div[3]/div[1]/div[3]/div[2]/div/a')
            phone_element_href = phone_element.get_attribute('href')
            if("tel" in phone_element_href):
                phone = phone_element.text

        except Exception as e:
            print("can't find phone")

        print("phone --> ", phone)

        # find rating
        rating = 0
        rating_count = 0
        try:
            WebDriverWait(accommodation_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'dGsKv')))
            rating_container = accommodation_page_driver.find_element(By.CLASS_NAME, 'dGsKv')
            
            rating_element = rating_container.find_element(By.CLASS_NAME, 'kJyXc')
            rating = float(rating_element.text)

            rating_count_element = rating_container.find_element(By.CLASS_NAME, 'KxBGd')
            rating_count = int(rating_count_element.text.replace(',', '').replace('รีวิว ', '').replace(' รายการ', ''))

        except Exception as e:
            print("can't find rating and rating_count")

        print("rating --> ", rating)
        print("rating_count --> ", rating_count)

        # find facilities, tags
        facilities = []
        tags = []
        try:
            target_xpath = [
                '//*[@id="ABOUT_TAB"]/div[2]/div[2]/div[2]', # //*[@id="ABOUT_TAB"]/div[2]/div[2]/div[2]
                '//*[@id="ABOUT_TAB"]/div[2]/div[2]/div[5]', # //*[@id="ABOUT_TAB"]/div[2]/div[2]/div[5]
                '//*[@id="ABOUT_TAB"]/div[2]/div[2]/div[8]'  # //*[@id="ABOUT_TAB"]/div[2]/div[2]/div[8]
            ]
            Idx_target = 0
            Idx_topic = 0
            
            WebDriverWait(accommodation_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'vqEpQ')))
            all_topic_elements = accommodation_page_driver.find_elements(By.CLASS_NAME, 'vqEpQ')
            fixed_topic = ["สิ่งอำนวยความสะดวกของสถานที่ให้บริการ", "สิ่งอำนวยความสะดวกในห้องพัก", "ประเภทห้องพัก"]

            while(Idx_target < len(target_xpath)):
                try:
                    WebDriverWait(accommodation_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, target_xpath[Idx_target])))
                    target_container = accommodation_page_driver.find_element(By.XPATH, target_xpath[Idx_target])

                    cur_topic = all_topic_elements[Idx_topic].text
                    print("cur_topic --> ", cur_topic)

                    if(cur_topic not in fixed_topic):
                        Idx_topic += 1
                        continue

                    if(cur_topic == "สิ่งอำนวยความสะดวกของสถานที่ให้บริการ" or cur_topic == "สิ่งอำนวยความสะดวกในห้องพัก"):
                        all_facility_elements = target_container.find_elements(By.CLASS_NAME, 'gFttI')
                        for cur_facility_element in all_facility_elements:
                            cur_facility_text = cur_facility_element.text
                            if(not len(cur_facility_text)):
                                continue
                            facilities.append(cur_facility_text)

                    elif(cur_topic ==  "ประเภทห้องพัก"):
                        all_tag_elements = target_container.find_elements(By.CLASS_NAME, 'gFttI')
                        for cur_tag_element in all_tag_elements:
                            cur_tag_text = cur_tag_element.text
                            if(not len(cur_tag_text)):
                                continue                        
                            tags.append(cur_tag_text)
                
                except Exception as e:
                    pass

                Idx_target += 1
                Idx_topic += 1

        except Exception as e:
            print("can't find facilities or tags")

        print("facilities --> ", facilities)
        print("tags --> ", tags)

        # find star
        star = 0
        try:
            WebDriverWait(accommodation_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'JXZuC')))
            star_container = accommodation_page_driver.find_element(By.CLASS_NAME, 'JXZuC')
            star_element = star_container.find_element(By.TAG_NAME, 'title')
            star = star_element.text.split(' ')[0]

        except Exception as e:
            print("can't find star")

        print("star --> ", star)


        # convert accommodation url to adjust page url
        # for example: from 'https://th.tripadvisor.com/Hotel_Review-g10804710-d586602-Reviews-Pacific_Club_Resort-Karon_Beach_Karon_Phuket.html' to 'https://th.tripadvisor.com/ImproveListing-d586602.html'
        link_to_adjust_page = 'https://th.tripadvisor.com/ImproveListing-%s.html' % (link_to_accommodation.split('-')[2])

        # ** find lat/long, location data and openingHours (there are in another page of current accommodation)
        # ** if this accommodation not have lat/long
        # ** don't continue to scrape
        lat, long, types = scrape_location_latlong_types(
            accommodation_page_driver = accommodation_page_driver,
            link_to_adjust_page = link_to_adjust_page
        )
        
        # **if can't find lat/long --> don't scrape this attaction
        if(lat == 0 and long == 0):
            print("in scrape_single_accommodation --> can't find lat/long --> don't scrape this accommodation ...")
            accommodation_page_driver.quit()
            return Accommodation()


        # find location
        location = scrape_location(
            accommodation_page_driver = accommodation_page_driver,
            latitude = lat,
            longitude = long,
            province_th = province_th
        )
        print("province :", location.get_province_code(), location.get_province())
        print("District :", location.get_district_code(), location.get_district())
        print("Address : ", location.get_address())


        # find img_path
        img_path = scrape_img(accommodation_page_driver)
        print("cur img path -> ", img_path)

        # set some of "accommodation" object properties
        accommodation.set_name(name)
        accommodation.set_description(description)
        accommodation.set_phone(phone)
        accommodation.set_latitude(lat)
        accommodation.set_longitude(long)
        accommodation.set_imgPath(img_path)
        accommodation.set_website(link_to_accommodation)
        accommodation.set_facility(facilities)
        accommodation.set_tag(tags)
        accommodation.set_type(types)
        accommodation.set_star(star)
        accommodation.set_location(
            address = location.get_address(),
            province = location.get_province(),
            district = location.get_district(),
            sub_district = location.get_sub_district(),
            province_code = location.get_province_code(),
            district_code = location.get_district_code(),
            sub_district_code = location.get_sub_district_code()
        )
        accommodation.set_rating(
            score = rating,
            rating_count = rating_count
        )

        accommodation_page_driver.quit()
        break

    return accommodation


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

        # find group of accommodation on the nth page
        all_accommodations_card = []

        # retry in case of web restrictions and some elements not loaded
        try:
            query_url_by_page = convert_url_by_page(
                link_to_accommodation = query_url,
                page = page
            )
            driver.get(query_url_by_page)
            # scroll and wait for some msec
            driver.execute_script('window.scrollBy(0, document.body.scrollHeight)')
            
            print("check current page url --> ", driver.current_url)

            # wait for div (each accommodation section) to be present and visible
            print("b1 part 1")
            print("debug get_all_url_by_page: accommodation by one page section")
            WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'jhsNf')))
            all_accommodations_card = driver.find_elements(By.CLASS_NAME, 'jhsNf')

            # if current page is 1, find button "ดูทั้งหมด"(if it exist) --> click to load more accommodation card elements
            # assume that page 1 of target province (phuket for now) not less than 10
            # if(page == 1 and len(all_accommodations_card) <= 10):
            #     print("b 0.5")
            #     print("debug get_all_url_by_page: get click more btn for page 1")
            #     WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'sOtnj')))
            #     click_more_btn = driver.find_element(By.CLASS_NAME, 'sOtnj')
            #     click_more_btn.click()

            #     # wait for div (each accommodation section) to be present and visible
            #     print("b1 part 2")
            #     print("debug get_all_url_by_page: accommodation by one page section")
            #     WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'jhsNf')))
            #     all_accommodations_card = driver.find_elements(By.CLASS_NAME, 'jhsNf')

            # check if all accomodation card can get tag a and its attribute for url
            print("b2")
            print("check in loop ...")
            for cur_accommodation_card in all_accommodations_card:

                cur_accommodation_url = cur_accommodation_card.find_element(By.TAG_NAME, 'a').get_attribute('href')
                print("cur_accommodation_url : ", cur_accommodation_url)
                res_url_by_page.append(cur_accommodation_url)
            
            driver.quit()
            break
            
        except Exception as e:
            print("retry find get_all_url_by_page ...")
            cnt_retry += 1
            driver.quit()
            continue

    return res_url_by_page.copy()


def mulProcess_helper_scrape_accommodations_by_province(page: int, province_url: str, province: str) -> pd.DataFrame:
    # res_accommodation_df = pd.DataFrame()
    res_accommodation_df = create_accommodation_df(Accommodation())
    
    cnt_for_debug = 0
        
    print("scraping accommodation | province --> %s | page --> %s" % (province, page))

    all_url_by_page = get_all_url_by_page(query_url = province_url, page = page)

    try:
        # use data from 'res_get_data_by_page' to retrive data of specific accommodation
        for cur_accommodation_url in all_url_by_page:
            # just use to limit amount of place --> will be removed 
            if(cnt_for_debug == 5):
                break

            # continue scraping data for a specific resgtaurant
            cur_accommodation = scrape_single_accommodation(
                link_to_accommodation = cur_accommodation_url,
                province_th = province
            )

            cnt_for_debug += 1

            # create data frame represent data scrape from current accommodation card
            cur_accommodation_df = create_accommodation_df(accommodation=cur_accommodation)

            # concat all data frame result
            res_accommodation_df = pd.concat([res_accommodation_df, cur_accommodation_df])

    except Exception as e:
        pass

        
    return res_accommodation_df.iloc[1:, :].copy()