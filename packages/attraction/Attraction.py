import sys
import os
sys.path.append('.')
from packages.attraction.AttractionTag import *
from packages.location.Location import *
from packages.rating.Rating import *

class Attraction:
    def __init__(self) -> None:
        self.__name = ''
        self.__description = ''
        self.__latitude = 0
        self.__longitude = 0
        self.__imgPath = []
        # attraction tags object
        self.__attractionTag = AttractionTag()
        # location object
        self.__location = Location()
        # rating object
        self.__rating = Rating()
        

    ## define getter methods
    
    def get_name(self) -> str:
        return self.__name
    
    def get_description(self) -> str:
        return self.__description
    
    def get_latitude(self) -> float:
        return self.__latitude
    
    def get_longitude(self) -> float:
        return self.__longitude
    
    def get_imgPath(self) -> list[str]:
        return self.__imgPath
    
    def get_attractionTag(self) -> AttractionTag:
        return self.__attractionTag
    
    def get_location(self) -> Location:
        return self.__location
    
    def get_rating(self) -> Rating:
        return self.__rating


    ## define getter methods
    def set_name(self, name:str) -> None:
        self.__name = name
    
    def set_description(self, description:str) -> None:
        self.__description = description        
    
    def set_latitude(self, latitude:str) -> None:
        self.__latitude = latitude
    
    def set_longitude(self, longitude:str) -> None:
        self.__longitude = longitude
    
    def set_imgPath(self, imgPath:list[str]) -> None:
        self.__imgPath = imgPath.copy()