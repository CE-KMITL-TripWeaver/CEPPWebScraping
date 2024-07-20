import sys
import os
sys.path.append('.')
from AttractionTag import *
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
        self.rating = Rating()
        