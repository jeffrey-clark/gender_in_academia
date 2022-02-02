# import dependencies
import os, re, io, sys
import pandas as pd
#import mysql.connector
import json
import numpy as np

# import function collections
from Functions.j_functions import *
from Functions.language import *
from Functions.functions import *

# set universal variables

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

pref_order = ['app_id', 'name', 'surname', 'financier', 'keywords', 'keyword_lang']

nonelist = ['None', 'NA', 'N/A', '-', '', ' ', '--', "null", "N.A.", ]

