import sys
import os
import shutil
import glob
import pandas as pd
import numpy as np

sys.path.append('.')

import constants.constants as const
import constants.file_handler_constants as fh

def createDirectory(parent_dir:str, dir_name:str):
    path = os.path.join(parent_dir, dir_name) 
    try: 
        os.makedirs(path, exist_ok = True) 
        print("Directory {0} created successfully".format(dir_name)) 
    except Exception as e: 
        print("Directory {0} can not be created".format(dir_name)) 

def removeNoneEmptyDir(dir:str):
    try:
        shutil.rmtree(dir, ignore_errors=False, onerror=None)
    except Exception as e:
        print("can not remove {}".format(dir))