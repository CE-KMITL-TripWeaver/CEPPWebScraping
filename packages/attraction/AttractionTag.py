class AttractionTag:
    def __init__(self) -> None:
        self.__tag_score = {
            "Tourism"       : 0,						
            "Adventure"     : 0,					
            "Meditation"	: 0,			
            "Art"           : 0,
            "Cultural"      : 0,
            "Landscape"     : 0,
            "Nature"        : 0,
            "Historical"    : 0,
            "Cityscape"     : 0,
            "Beach"         : 0,
            "Mountain"      : 0,
            "Architecture"  : 0,
            "Temple"        : 0,
            "WalkingStreet" : 0,
            "Market"        : 0,
            "Village"       : 0,
            "NationalPark"  : 0,
            "Diving"        : 0,
            "Snuggle"       : 0,
            "Waterfall"     : 0,
            "Island"        : 0,
            "Shopping"      : 0,
            "Camping"       : 0,
            "Fog"           : 0,
            "Cycling"       : 0,
            "Monument"      : 0,
            "Zoo"           : 0,
            "Waterpark"     : 0,
            "Hiking"        : 0,
            "Museum"        : 0,
            "Riverside"     : 0,
            "NightLife"     : 0,
            "Family"        : 0,
            "Kid"           : 0,
            "Landmark"      : 0,
            "Forest"        : 0,
        }


    ## define getter method

    def get_tag_score(self, key:str) -> float:
        return self.__tag_score.get(key, -1)
    
    
    ## define setter method

    def set_tag_score(self, key:str, val:float) -> None:
        if(self.get_tag_score(key) == -1):
            return
        self.__tag_score[key] = val
        
        