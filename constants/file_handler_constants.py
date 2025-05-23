import os

# user have to project directory path such as r"C:\Users\user\git\CEPPWebScraping"

path_to_proj = r"C:\Users\user\git\CEPPWebScraping"

### declare variables which will use to find constant path ###

# path for constants used in this project
STORE_CONSTS = os.path.join(path_to_proj, 'constants')

### declare variables which will use find packages path ###

# path for packages used in this project
STORE_PACKAGES = os.path.join(path_to_proj, 'packages')


### declare variables which will use find geocode.csv ###

# path to 'geocode.csv'
PATH_TO_GEOCODE = os.path.join(path_to_proj, 'geocode.csv')


### path for destination to store result of 'attraction_scraping' ###

STORE_ATTRACTION_SCRAPING = os.path.join(path_to_proj, 'attraction_scraping')

### path for destination to store result of 'merge_attraction_scraping' ###

STORE_MERGE_ATTRACTION_SCRAPING = os.path.join(path_to_proj, 'merge_attraction_scraping')


### path for destination to store result of 'restaurant_scraping' ###

STORE_RESTAURANT_SCRAPING = os.path.join(path_to_proj, 'restaurant_scraping')

### path for destination to store result of 'merge_restaurant_scraping' ###

STORE_MERGE_RESTAURANT_SCRAPING = os.path.join(path_to_proj, 'merge_restaurant_scraping')


### path for destination to store result of 'accomodation_scraping' ###

STORE_ACCOMM_SCRAPING = os.path.join(path_to_proj, 'accommodation_scraping')

### path for destination to store result of 'merge_accommodation_scraping' ###

STORE_MERGE_ACCOMM_SCRAPING = os.path.join(path_to_proj, 'merge_accommodation_scraping')


### path for destination to store result of 'fill_attractionTag_score' ###

STORE_FILL_ATTRACTION_TAG_SCORE = os.path.join(path_to_proj, 'fill_attractionTag_score')
