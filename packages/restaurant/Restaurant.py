import sys
import os
sys.path.append('.')
from packages.location.Location import *
from packages.rating.Rating import *

class Restaurant:
    def __init__(self) -> None:
        self.__name = ''
        self.__sub_name = ''
        self.__type = []
        self.__facility = []
        self.__description = ''
        self.__latitude = 0
        self.__longitude = 0
        self.__imgPath = ['']
        self.__phone = ''
        self.__website = ''
        self.__openingHour = {}
        self.__priceRange = ''
        # location object
        self.__location = Location()
        # rating object
        self.__rating = Rating()
        

    ## define getter methods
    def get_name(self) -> str:
        return self.__name 

    def get_sub_name(self) -> str:
        return self.__sub_name 

    def get_type(self) -> list[str]:
        return self.__type.copy()
    
    def get_facility(self) -> list[str]:
        return self.__facility.copy()

    def get_description(self) -> str:
        return self.__description
    
    def get_latitude(self) -> float:
        return self.__latitude
    
    def get_longitude(self) -> float:
        return self.__longitude
    
    def get_imgPath(self) -> list[str]:
        return self.__imgPath.copy()

    def get_phone(self) -> str:
        return self.__phone
    
    def get_website(self) -> str:
        return self.__website

    def get_openingHour(self) -> dict:
        return self.__openingHour.copy()
    
    def get_priceRange(self) -> str:
        return self.__priceRange
    
    def get_location(self) -> Location:
        return self.__location
    
    def get_rating(self) -> Rating:
        return self.__rating
    

    ## define setter methods
    def set_name(self, name: str) -> None:
        self.__name = name

    def set_sub_name(self, sub_name: str) -> None:
        self.__sub_name = sub_name

    def set_type(self, type: list[str]) -> None:
        self.__type = type.copy()
    
    def set_facility(self, facility: list[str]) -> None:
        self.__facility = facility.copy()

    def set_description(self, description: str) -> None:
        self.__description = description
    
    def set_latitude(self, latitude: float) -> None:
        self.__latitude = latitude
    
    def set_longitude(self, longitude: float) -> None:
        self.__longitude = longitude
    
    def set_imgPath(self, imgPath: list[str]) -> None:
        self.__imgPath = imgPath.copy()

    def set_phone(self, phone:str) -> None:
        self.__phone = phone
    
    def set_website(self, website:str) -> None:
        self.__website = website

    def set_openingHour(self, openingHour: dict) -> None:
        self.__openingHour = openingHour.copy()
    
    def set_priceRange(self, priceRange: str) -> None:
        self.__priceRange = priceRange

    def set_location(self, address: str, province: str, district: str, sub_district: str, province_code: int, district_code: int, sub_district_code: int) -> None:
        self.__location.set_address(address)
        self.__location.set_province(province)
        self.__location.set_district(district)
        self.__location.set_sub_district(sub_district)
        self.__location.set_province_code(province_code)
        self.__location.set_district_code(district_code)
        self.__location.set_sub_district_code(sub_district_code)

    def set_rating(self, score: float, rating_count: int) -> None:
        self.__rating.set_score(score)
        self.__rating.set_ratingCount(rating_count) 