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


### path for destination to store result of 'restaurant_scraping' ###

STORE_RESTAURANT_SCRAPING = os.path.join(path_to_proj, 'restaurant_scraping')