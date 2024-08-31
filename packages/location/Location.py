class Location:
    def __init__(self) -> None:
        self.__address = ""
        self.__province = ""
        self.__district = ""
        self.__subDistrict = ""
        self.__province_code = 0
        self.__district_code = 0
        self.__sub_district_code = 0


    ## define getter methods
 
    def get_address(self) -> str:
        return self.__address

    def get_province(self) -> str:
        return self.__province
    
    def get_district(self) -> str:
        return self.__district
    
    def get_subDistrict(self) -> str:
        return self.__subDistrict
    
    def get_province_code(self) -> int:
        return self.__province_code
    
    def get_district_code(self) -> int:
        return self.__district_code
    
    def get_sub_district_code(self) -> int:
        return self.__sub_district_code
    

    ## define setter methods

    def set_address(self, address:str) -> None:
        self.__address = address

    def set_province(self, province:str) -> None:
        self.__province = province
    
    def set_district(self, district:str) -> None:
        self.__district = district
    
    def set_subDistrict(self, subDistrict:str) -> None:
        self.__subDistrict = subDistrict
    
    def set_province_code(self, province_code:int) -> None:
        self.__province_code = province_code
    
    def set_district_code(self, district_code:int) -> None:
        self.__district_code = district_code
    
    def set_sub_district_code(self, sub_district_code:int) -> None:
        self.__sub_district_code = sub_district_code 
