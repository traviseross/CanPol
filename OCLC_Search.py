#!/usr/bin/python3
# -*- coding: utf-8 -*-
#========== LIBRARIES ========== 
from bs4 import BeautifulSoup
import pandas as pd
import requests
# import pymarc
mydict = {58: 0, 59: 0, 44: 0, 46: 0, 39: 0, 96: 0, 38: 0, 63: 0, 145: 0, 146: 0, 147: 0, 148: 0, 130: 0, 146: 0, 147: 0, 148: 0, 130: 0}
#========== FUNCTIONS ========== 
# a function to search WorldCat for books
def process_books(row):
    ''' (str,str) -> str
    take a list of authors and a publication title, output a worldcat search opensearch query with combined authors and title
    '''
    pub_int = row['year']
    pub_date = str(pub_int)
    pub_title = row['name']
    pub_title = pub_title.translate(mydict)
    #pub_title = 'srw.ti+=+"' + pub_title +'"'
    authors = []
    for auth in ['a1','a2','a3','a4','a5','a6']:
        try:
            auth_surname = row[auth].split(',')[0].strip()
        except AttributeError:
            auth_surname = None
        if auth_surname != None:
           authors.append(auth_surname)
    #author_list = "srw.au+=+" + "+and+srw.au+=+".join(authors)
    author_list = " ".join(authors)
    query_string = pub_title + "+and+" + author_list
    # query_URL = "http://www.worldcat.org/webservices/catalog/search/worldcat/opensearch?q=" + query_string + "&recordSchema=info%3Asrw%2Fschema%2F1%2Fmarcxml&servicelevel=default&frbrGrouping=on&wskey={built-in-api-key}"
    #query_URL = 'https://www.worldcat.org/search?q=ti:"' + pub_title + '"&dblist=638&fq=+(x0:book-+OR+(x0:book+x4:printbook)+-((x0:book+x4:digital))+-((x0:book+x4:mic))+-((x0:book+x4:thsis))+-((x0:book+x4:mss))+-((x0:book+x4:braille))+-((x0:book+x4:continuing)))+>+yr:' + pub_date
    query_URL = 'https://www.worldcat.org/search?q=ti:"' + pub_title + '"&fq=+(x0:book-+OR+(x0:book+x4:printbook)+-((x0:book+x4:digital))+-((x0:book+x4:mic))+-((x0:book+x4:thsis))+-((x0:book+x4:mss))+-((x0:book+x4:braille))+-((x0:book+x4:continuing)))+yr:' + pub_date
    print(query_URL)
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

