from ...interface.location import Location
from ...interface.rating import Rating

class Accommodation(object):
    
    def __init__(self):
        self.name = ""
        self.description = ""
        self.type = []
        self.tags = []
        self.facilities = []
        self.latitude = 0
        self.longitude = 0
        self.location = Location()
        self.imgPath = []
        self.rating = Rating()
        self.star = 0
        self.contact = "test contact"
        self.publicTransportation = []
        self.minPrice = 0