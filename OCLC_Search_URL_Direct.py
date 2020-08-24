#!/usr/bin/python3
# -*- coding: utf-8 -*-
#========== LIBRARIES ========== 
from bs4 import BeautifulSoup
import pandas as pd
import requests
# import pymarc

#========== FUNCTIONS ========== 
# a function to search WorldCat for books
def process_books(row):
    ''' (str,str) -> str
    take a list of authors and a publication title, output a worldcat search opensearch query with combined authors and title
    '''
    pub_title = row['name']
    pub_title = 'srw.ti+' + pub_title
    authors = []
    for auth in ['a1','a2','a3','a4','a5','a6']:
        try:
            auth_surname = row[auth].split(',')[0].strip()
        except AttributeError:
            auth_surname = None
        if auth_surname != None:
           authors.append(auth_surname)
    author_list = "srw.au+" + "+and+srw.au+".join(authors)
    query_string = pub_title + "+and+" + author_list
    print(query_string)
    ######################

# a function to search for DOIs for article
def process_articles(row):
    pub_title = row['name']
   # print(pub_title,'is an article')

#a function to handle what's left, hopefully
def process_other(row):
    pub_title = row['name']
   # print(pub_title,' is something else')

#========== MAIN ========== 
# open the data from excel, store it in a dataframe
full_data = pd.read_excel('../Data/PS_Data.xlsx')
# iterate through each row, run the appropriate function per publication type
for i,row in full_data.iterrows():
    if row['pub_type'] == 1:
        publication = process_articles(row)
    elif row['pub_type'] == 2:
        publication = process_books(row)
    else:
        publication = process_other(row)