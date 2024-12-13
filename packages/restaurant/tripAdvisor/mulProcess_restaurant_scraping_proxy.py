from selenium import webdriver
import re
import sys
sys.path.append('.')
import constants.constants as const
import constants.file_handler_constants as fh
from constants.restaurant_constants import *

from packages.restaurant.Restaurant import *
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
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.options import Options


from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_restaurant_df(restaurant: Restaurant) -> pd.DataFrame:
    restaurant_dict = {
        'name' : [restaurant.get_name()],
        'description' : [restaurant.get_description()],
        'priceRange' : [restaurant.get_priceRange()],
        'latitude' : [restaurant.get_latitude()],
        'longitude' : [restaurant.get_longitude()],
        'imgPath' : [restaurant.get_imgPath()],
        'phone': [restaurant.get_phone()],
        'website': [restaurant.get_website()],
        'openingHour': [restaurant.get_openingHour()],
        'facility': [restaurant.get_facility()],
        'type': [restaurant.get_type()],

        # location
        'address' : [restaurant.get_location().get_address()],
        'province' : [restaurant.get_location().get_province()],
        'district' : [restaurant.get_location().get_district()],
        'subDistrict' : [restaurant.get_location().get_sub_district()],
        'province_code' : [restaurant.get_location().get_province_code()],
        'district_code' : [restaurant.get_location().get_district_code()],
        'sub_district_code' : [restaurant.get_location().get_sub_district_code()],

        # rating
        'score' : [restaurant.get_rating().get_score()],
        'ratingCount' : [restaurant.get_rating().get_ratingCount()],
    }

    restaurant_df = pd.DataFrame(restaurant_dict)
    
    return restaurant_df.copy()



def convert_url_by_page(link_to_restaurant: str, page: int) -> str:
    
    first_page_url_split = link_to_restaurant.split('-')
    nth_count_page = 'oa%s' % ((page - 1) * 30)
    first_page_url_split[-1] = nth_count_page
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


def scrape_img(restaurant_page_driver: webdriver) -> list[str]:

    res_imgPath = []

    possible_click_img_xpath = [
        '//*[@id="lithium-root"]/main/div/div[6]/div/div[1]/div[2]/div/div/div/div[1]/div/div/div[3]/button',
        '//*[@id="lithium-root"]/main/div/div[6]/div/div[1]/div[2]/div/div/div/div/div/div/div[3]/button'
    ]
    
    btn_img_xpath = ""
    print('y2')
    for cur_xpath in possible_click_img_xpath:
        try:
            WebDriverWait(restaurant_page_driver, 2).until(EC.visibility_of_element_located((By.XPATH, cur_xpath)))
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
        # WebDriverWait(restaurant_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, btn_img_xpath)))
        print('y3')
        click_img_btn = restaurant_page_driver.find_element(By.XPATH, btn_img_xpath)

        # Move to the element and click
        print("y4")
        actions = ActionChains(restaurant_page_driver)
        actions.move_to_element(click_img_btn).click().perform()
        print("y5")
        
        print("cur img url --> ", restaurant_page_driver.current_url)

        type_value = extract_type_from_url(url=restaurant_page_driver.current_url)
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
                    WebDriverWait(restaurant_page_driver, 2).until(EC.visibility_of_element_located((By.CLASS_NAME, 'BtGfv')))
                    all_img_containers = restaurant_page_driver.find_elements(By.CLASS_NAME, 'BtGfv')
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
                    WebDriverWait(restaurant_page_driver, 2).until(EC.visibility_of_element_located((By.CLASS_NAME, 'cfCAA')))
                    all_img_elements = restaurant_page_driver.find_elements(By.CLASS_NAME, 'cfCAA')
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
       

def scrape_location(restaurant_page_driver: webdriver, latitude: float, longitude: float, province_th: str) -> Location:

    # find better address description on wongnai
    # for example: "991 ถนนพระราม 1 Pathum Wan, กรุงเทพมหานคร (กทม.) 10330 ไทย"
    address_tripAdvisor = ""
    possible_address_xpath = [
        '//*[@id="lithium-root"]/main/div/div[3]/div/div[3]/span[1]/span[2]/button/span',
        '//*[@id="lithium-root"]/main/div/div[3]/div/div[3]/span[1]/span[2]/button/span',
    ]

    for cur_address_xpath in possible_address_xpath:
        try:
            WebDriverWait(restaurant_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, cur_address_xpath)))
            address_element = restaurant_page_driver.find_element(By.XPATH, cur_address_xpath)
            address_tripAdvisor = address_element.text
            
        except Exception as e:
            print("can't find address_tripAdvisor")


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
    

# scrape lat/long, openingHours, types, facilities (there are in adjust page of current restaurant: 'https://th.tripadvisor.com/ImproveListing-d1792735.html')
def scrape_adjust_page(restaurant_page_driver: webdriver, link_to_adjust_page: str) -> tuple[float, float, dict, list[str], list[str]]:
    lat = 0
    long = 0
    openingHours = {}
    types = []
    facilities = []
    
    # create new webdriver to continue scrape lat/long, openingHours in adjust restaurant page
    cnt_retry = 0
    
    while(True):
        if(cnt_retry == 10):
            print("max retry for scrape single restaurant ...")
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

        # set Chrome options to run in headless mode
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("--lang=th-TH")
        # options.add_argument("--headless=new")
        options.add_experimental_option(
            "prefs", 
            {
                "profile.managed_default_content_settings.images": 2, # Disable image
                # "profile.default_content_setting_values.cookies": 2,  # Block all cookies
                "profile.default_content_settings.popups": 0,         # Disable popups
                # "profile.managed_default_content_settings.cookies": 2  # Disable third-party cookies
            }
        )

        # initialize the Chrome driver with service, selenium-wire options, and chrome options
        adjust_page_driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            seleniumwire_options=seleniumwire_options,
            options=options
        )
        
        # retry in case of web restrictions, some elements not loaded
        try:
            print("scrape data in adjust restaurant page...")
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


        # scroll and wait for some msec
        adjust_page_driver.execute_script('window.scrollBy(0, document.body.scrollHeight)')

        # find lat/long
        try:
            WebDriverWait(adjust_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lithium-root"]/main/div[2]/div[3]/div[1]/div/div[2]/div[2]/div/div/div[2]/div/div/div[3]/div[1]/div/div[2]/div/div/div/span')))
            WebDriverWait(adjust_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lithium-root"]/main/div[2]/div[3]/div[1]/div/div[2]/div[2]/div/div/div[2]/div/div/div[3]/div[2]/div/div[2]/div/div/div/span')))
    
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
            return lat, long, openingHours.copy(), types.copy(), facilities.copy()

        # wiat for element of types and facilities to load
        time.sleep(5)

        # find type
        try:     
            # find restaurant types container
            WebDriverWait(adjust_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'IBVyx')))

            possible_type_container = adjust_page_driver.find_elements(By.CLASS_NAME, 'IBVyx')
            type_container = None
            for cur_element in possible_type_container[::-1]:
                cur_text = cur_element.text
                if("หมวดหมู่อาหาร" in cur_text):
                    type_container = cur_element
                    WebDriverWait(adjust_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'vvmrG')))
                    all_type_element = type_container.find_elements(By.CLASS_NAME, 'vvmrG')
                    for cur_type in all_type_element:
                        cur_text = cur_type.text
                        types.append(cur_text)

        except Exception as e:
            print("can't find types")

        print("types --> ", types)


        # find facilities
        try:
            # find restaurant facilities container
            # AoddJ
            WebDriverWait(adjust_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'mowmC')))
            possible_facility_container = adjust_page_driver.find_elements(By.CLASS_NAME, 'mowmC')
            facility_container = None
            for cur_element in possible_facility_container[::-1]:
                cur_text = cur_element.text
                # print("check facility cur_text --> ", cur_text)

                if("สิ่งอำนวยความสะดวก" in cur_text):
                    facility_container = cur_element
                    WebDriverWait(adjust_page_driver, 2).until(EC.visibility_of_element_located((By.CLASS_NAME, 'PMWyE')))
                    # time.sleep(16)
                    
                    checkbox_containers = facility_container.find_elements(By.CLASS_NAME, 'PMWyE')
                    print("check len faci  len --> ", len(checkbox_containers))
                    for Idx in range(len(checkbox_containers)):
                        cur_checkbox = checkbox_containers[Idx].find_element(By.TAG_NAME, 'span')
                        is_check = True if cur_checkbox.get_attribute('class') != 'U' else False
                        if(is_check):
                            facilities.append(ALL_RESTAURANTS_TRIPADVISOR_FACILITIES[Idx])

                    break

        except Exception as e:
            print("can't find facilities")

        print("facilities --> ", facilities)


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

        print("openingHours : ", openingHours)


        adjust_page_driver.quit()
        break

    return lat, long, openingHours.copy(), types.copy(), facilities.copy()


def scrape_single_restaurant(link_to_restaurant: str, province_th: str) -> Restaurant:
    
    restaurant = Restaurant()
    cnt_retry = 0
    
    while(True):
        if(cnt_retry == 10):
            print("max retry for scrape single restaurant ...")
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
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("--lang=th-TH")
        options.add_experimental_option(
            "prefs", 
            {
                "profile.managed_default_content_settings.images": 2, # Disable image
                # "profile.default_content_setting_values.cookies": 2,  # Block all cookies
                "profile.default_content_settings.popups": 0,         # Disable popups
                # "profile.managed_default_content_settings.cookies": 2  # Disable third-party cookies
            }
        )

        # initialize the web driver with service, selenium-wire options, and web browser options
        # update: just change browser to chrome driver since priceRange can not be found in Edge
        restaurant_page_driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            seleniumwire_options=seleniumwire_options,
            options=options
        )
        
        # retry in case of web restrictions and some elements not loaded
        try:
            print("******************************************************")
            print("scrape single restaurant...")
            print("for restaurant : ", link_to_restaurant)
            restaurant_page_driver.get(link_to_restaurant)
            # restaurant_page_driver.add_cookie()

            print("debug scrape_single_restaurant: top info component section")
            # WebDriverWait(restaurant_page_driver, 2).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lithium-root"]/main/span/div[4]/div/div[1]/div[3]/div')))
            # top_info_container = restaurant_page_driver.find_element(By.XPATH, '//*[@id="lithium-root"]/main/span/div[4]/div/div[1]/div[3]/div')

            print("debug scrape_single_restaurant: bottom info component section")
            WebDriverWait(restaurant_page_driver, 2).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lithium-root"]/main/div/div[6]/div/div[2]')))
            bottom_info_container = restaurant_page_driver.find_element(By.XPATH, '//*[@id="lithium-root"]/main/div/div[6]/div/div[2]')

            print("debug scrape_single_restaurant: common component section")
            WebDriverWait(restaurant_page_driver, 2).until(EC.visibility_of_element_located((By.CLASS_NAME, 'IDaDx')))

        except Exception as e:
            print("retry single restaurant case 1...")
            cnt_retry += 1
            restaurant_page_driver.quit()
            continue
        
    
        # find name
        name = ""
        try:
            WebDriverWait(restaurant_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'rRtyp')))
            name_element = restaurant_page_driver.find_element(By.CLASS_NAME, 'rRtyp')
            name = name_element.text

        except Exception as e:
            print("can't find name")

        print("name -> ", name)

        # find description
        # description = ""
        # try:
        #     try:
        #         # find button to click readmore (if it exists, it likely to be the first elements of class 'lszDU')
        #         WebDriverWait(restaurant_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lszDU')))
        #         click_readmore_btn = restaurant_page_driver.find_element(By.CLASS_NAME, 'lszDU')
        #         click_readmore_btn.click()

        #     except Exception as e:
        #         pass

        #     WebDriverWait(restaurant_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'zYHGB')))
        #     all_description_elements = restaurant_page_driver.find_elements(By.CLASS_NAME, 'zYHGB')
        #     for cur_element in all_description_elements:
        #         cur_text =  cur_element.text
        #         if(len(cur_text)):
        #             description += cur_text + '\n'
            
        # except Exception as e:
        #     print("can't find description")

        # print("description -> ", description)
        

        # find priceRange
        priceRange = ""
        try:
            WebDriverWait(restaurant_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'XKqDZ')))
            detail_container = restaurant_page_driver.find_element(By.CLASS_NAME, 'XKqDZ')

            possible_priceRange_container = detail_container.find_elements(By.TAG_NAME, 'div')
            for cur_element in possible_priceRange_container:
                cur_text = cur_element.text
                print("check price cur_text --> ", cur_text)
                if("ช่วงราคา" in cur_text):
                    priceRange_element = cur_element.find_element(By.CLASS_NAME, 'hmDzD')
                    priceRange = priceRange_element.text
                    print("found priceRange --> ", priceRange)
                    break

        except Exception as e:
            print("can't find priceRange")

        print("priceRange --> ", priceRange)


        # find phone
        phone = ""
        try:
            WebDriverWait(restaurant_page_driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lithium-root"]/main/div/div[3]/div/div[3]/span[2]/span[2]/a')))
            phone_element = restaurant_page_driver.find_element(By.XPATH, '//*[@id="lithium-root"]/main/div/div[3]/div/div[3]/span[2]/span[2]/a')
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
            WebDriverWait(restaurant_page_driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'sOyfn')))
            rating_container = restaurant_page_driver.find_element(By.CLASS_NAME, 'sOyfn')
            
            rating_element = rating_container.find_element(By.CLASS_NAME, 'uuBRH')
            rating = float(rating_element.text)

            rating_count_element = rating_container.find_element(By.CLASS_NAME, 'oXJmt')
            rating_count = int(rating_count_element.text.replace(',', '').replace('รีวิว ', '').replace(' รายการ', ''))

        except Exception as e:
            print("can't find rating and rating_count")

        print("rating --> ", rating)
        print("rating_count --> ", rating_count)


        # find img_path
        img_path = scrape_img(restaurant_page_driver)
        print("cur img path -> ", img_path)


        # convert restaurant url to adjust page url
        # for example: from 'https://th.tripadvisor.com/Restaurant_Review-g1210687-d1792735-Reviews-Kwong_Shop_Seafood-Kata_Beach_Karon_Phuket.html' to 'https://th.tripadvisor.com/ImproveListing-d586602.html'
        link_to_adjust_page = 'https://th.tripadvisor.com/ImproveListing-%s.html' % (link_to_restaurant.split('-')[2])

        # ** find lat/long, location data and openingHours (there are in another page of current restaurant)
        # ** if this restaurant not have lat/long
        # ** don't continue to scrape
        lat, long, openingHours, types, facilities = scrape_adjust_page(
            restaurant_page_driver = restaurant_page_driver,
            link_to_adjust_page = link_to_adjust_page
        )
        
        # **if can't find lat/long --> don't scrape this attaction
        if(lat == 0 and long == 0):
            print("in scrape_single_restaurant --> can't find lat/long --> don't scrape this restaurant ...")
            restaurant_page_driver.quit()
            return Restaurant()
        

        # find location
        location = scrape_location(
            restaurant_page_driver = restaurant_page_driver,
            latitude = lat,
            longitude = long,
            province_th = province_th
        )
        print("province :", location.get_province_code(), location.get_province())
        print("District :", location.get_district_code(), location.get_district())
        print("Address : ", location.get_address())


        # set some of "restaurant" object properties
        restaurant.set_name(name)
        # restaurant.set_description(description)
        restaurant.set_phone(phone)
        restaurant.set_latitude(lat)
        restaurant.set_longitude(long)
        restaurant.set_imgPath(img_path)
        restaurant.set_website(link_to_restaurant)
        restaurant.set_openingHour(openingHours)
        restaurant.set_type(types)
        restaurant.set_facility(facilities)
        restaurant.set_priceRange(priceRange)
        restaurant.set_location(
            address = location.get_address(),
            province = location.get_province(),
            district = location.get_district(),
            sub_district = location.get_sub_district(),
            province_code = location.get_province_code(),
            district_code = location.get_district_code(),
            sub_district_code = location.get_sub_district_code()
        )
        restaurant.set_rating(
            score = rating,
            rating_count = rating_count
        )

        restaurant_page_driver.quit()
        break

    return restaurant


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

        # find group of restaurant on the nth page
        all_restaurants_card = []

        # retry in case of web restrictions and some elements not loaded
        try:
            query_url_by_page = convert_url_by_page(
                link_to_restaurant = query_url,
                page = page
            )
            driver.get(query_url_by_page)
            # scroll and wait for some msec
            driver.execute_script('window.scrollBy(0, document.body.scrollHeight)')
            
            print("check current page url --> ", driver.current_url)

            # wait for div (each restaurant section) to be present and visible
            print("b1 part 1")
            print("debug get_all_url_by_page: restaurant by one page section")
            WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CLASS_NAME, 'tbrcR')))
            all_restaurants_card = driver.find_elements(By.CLASS_NAME, 'tbrcR')


            # check if all accomodation card can get tag a and its attribute for url
            print("b2")
            print("check in loop ...")
            for cur_restaurant_card in all_restaurants_card:

                cur_restaurant_url = cur_restaurant_card.find_element(By.TAG_NAME, 'a').get_attribute('href')
                print("cur_restaurant_url : ", cur_restaurant_url)
                res_url_by_page.append(cur_restaurant_url)
            
            driver.quit()
            break
            
        except Exception as e:
            print("retry find get_all_url_by_page ...")
            cnt_retry += 1
            driver.quit()
            continue

    return res_url_by_page.copy()


def mulProcess_helper_scrape_restaurants_by_province(page: int, province_url: str, province: str) -> pd.DataFrame:
    
    res_restaurant_df = create_restaurant_df(Restaurant())
    
    cnt_for_debug = 0
        
    print("scraping restaurant | province --> %s | page --> %s" % (province, page))

    all_url_by_page = get_all_url_by_page(query_url = province_url, page = page)

    # use data from 'res_get_data_by_page' to retrive data of specific restaurant
    # print(all_url_by_page[0:len(all_url_by_page)//2])
    # print(all_url_by_page[len(all_url_by_page)//2:])

    # now scrape for half amount of restaurant
    for cur_restaurant_url in all_url_by_page[len(all_url_by_page)//2:]:
        # just use to limit amount of place --> will be removed 
        # if(cnt_for_debug == 2):
        #     break

        # continue scraping data for a specific resgtaurant
        cur_restaurant = scrape_single_restaurant(
            link_to_restaurant = cur_restaurant_url,
            province_th = province
        )

        cnt_for_debug += 1

        # create data frame represent data scrape from current restaurant card
        cur_restaurant_df = create_restaurant_df(restaurant=cur_restaurant)

        # concat all data frame result
        res_restaurant_df = pd.concat([res_restaurant_df, cur_restaurant_df])
    
    return res_restaurant_df.iloc[1:, :].copy()


###########################

def test_mulProcess_helper(page_number: int, province: str, wongnai_regionId: str) -> str:

    # res_restaurant_df = pd.DataFrame()
    res_restaurant_df = create_restaurant_df(Restaurant())
    
    print("scraping restaurant | province --> %s | page --> %s" % (province, page_number))
    cur_query_url = "https://www.wongnai.com/restaurants?categoryGroupId=9&regions=%s&page.number=%s" % (wongnai_regionId, page_number)
    return cur_query_url