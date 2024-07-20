class Rating:
    def __init__(self) -> None:
        self.__score = 0
        self.__ratingCount = 0


    ## define getter methods
    
    def get_score(self) -> float:
        return self.__score
    
    def get_ratingCount(self) -> int:
        return self.__ratingCount


    ## define getter methods

    def set_score(self, score:float) -> None:
        self.__score = score
    
    def set_ratingCount(self, ratingCount:int) -> None:
        self.__ratingCount = ratingCount