class AttractionTag:
    def __init__(self) -> None:
        self.__tag_score = {
            "Tourism"       : 0.0,						
            "Adventure"     : 0.0,					
            "Meditation"	: 0.0,			
            "Art"           : 0.0,
            "Cultural"      : 0.0,
            "Landscape"     : 0.0,
            "Nature"        : 0.0,
            "Historical"    : 0.0,
            "Cityscape"     : 0.0,
            "Beach"         : 0.0,
            "Mountain"      : 0.0,
            "Architecture"  : 0.0,
            "Temple"        : 0.0,
            "WalkingStreet" : 0.0,
            "Market"        : 0.0,
            "Village"       : 0.0,
            "NationalPark"  : 0.0,
            "Diving"        : 0.0,
            "Snuggle"       : 0.0,
            "Waterfall"     : 0.0,
            "Island"        : 0.0,
            "Shopping"      : 0.0,
            "Camping"       : 0.0,
            "Fog"           : 0.0,
            "Cycling"       : 0.0,
            "Monument"      : 0.0,
            "Zoo"           : 0.0,
            "Waterpark"     : 0.0,
            "Hiking"        : 0.0,
            "Museum"        : 0.0,
            "Riverside"     : 0.0,
            "NightLife"     : 0.0,
            "Family"        : 0.0,
            "Kid"           : 0.0,
            "Landmark"      : 0.0,
            "Forest"        : 0.0,
        }


    ## define getter method
    def get_attractionTag(self) -> dict:
        return self.__tag_score

    def get_tag_score(self, key:str) -> float:
        return self.__tag_score.get(key, -1)
    
    
    ## define setter method

    def set_attractionTag(self, attractionTag: dict) -> None:
        self.__tag_score = attractionTag.copy()

    def set_tag_score(self, key:str, val:float) -> None:
        if(self.get_tag_score(key) == -1):
            return
        self.__tag_score[key] = val
    
    