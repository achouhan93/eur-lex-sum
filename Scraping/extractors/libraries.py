# Importing Libraries
import os
import re
import pandas as pd
from time import sleep, time

import logging

# Libraries to deal with Web Scrapping
import urllib.request
import requests
from bs4 import BeautifulSoup

# For Uni Heidelberg Server
from opensearchpy import OpenSearch

''' Set the maximum depth of the Python interpreter stack to 100000. 
This limit prevents infinite recursion from causing an overflow of the C stack and crashing Python.'''
import sys
sys.setrecursionlimit(100000)

from tqdm import tqdm

import PyPDF2