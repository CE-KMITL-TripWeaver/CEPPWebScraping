import sys
sys.path.append('.')
import constants.file_handler_constants as fh
from packages.attraction.Attraction import *
import os
import glob
import time
import pandas as pd
import numpy as np

def test_list(arr:list):
    arr[1] = 44

x = [1,2,3]
test_list(x.copy())
print(x)
