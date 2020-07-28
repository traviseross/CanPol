#!/usr/bin/python3
# -*- coding: utf-8 -*-
#========== LIBRARIES ========== 
from bs4 import BeautifulSoup
import pandas as pd
import requests
import pymarc
import csv
#========== FUNCTIONS =======p=== 


#========== MAIN ========== 
from csv import reader

#open CSV file in read mode
with open ('books.corpus.csv','r') as read_obj:
    # now pass the file object to reader(), get the reader object
    csv_reader = reader(read_obj)
    #iterate by row
#    for row in csv_reader:
 #       r = requests.get(https://
