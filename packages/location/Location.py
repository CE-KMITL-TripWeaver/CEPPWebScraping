class Location:
    def __init__(self) -> None:
        self.__address = ""
        self.__province = ""
        self.__district = ""
        self.__subDistrict = ""
        self.__ISO_3166_code = 0
        self.__zip_code = 0
        self.__geo_code = 0


    ## define getter methods
 
    def get_address(self) -> str:
        return self.__address

    def get_province(self) -> str:
        return self.__province
    
    def get_district(self) -> str:
        return self.__district
    
    def get_subDistrict(self) -> str:
        return self.__subDistrict
    
    def get_ISO_3166_code(self) -> int:
        return self.__ISO_3166_code
    
    def get_zip_code(self) -> int:
        return self.__zip_code
    
    def get_geo_code(self) -> int:
        return self.__geo_code
    

    ## define setter methods

    def set_address(self, address:str) -> None:
        self.__address = address

    def set_province(self, province:str) -> None:
        self.__province = province
    
    def set_district(self, district:str) -> None:
        self.__district = district
    
    def set_subDistrict(self, subDistrict:str) -> None:
        self.__subDistrict = subDistrict
    
    def set_ISO_3166_code(self, ISO_3166_code:int) -> None:
        self.__ISO_3166_code = ISO_3166_code
    
    def set_zip_code(self, zip_code:int) -> None:
        self.__zip_code = zip_code
    
    def set_geo_code(self, geo_code:int) -> None:
        self.__geo_code = geo_code   
