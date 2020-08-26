#!/usr/bin/python3
# -*- coding: utf-8 -*-
#========== LIBRARIES ========== 
from bs4 import BeautifulSoup
import pandas as pd
import requests
# import pymarc
import re
punctuation_dict = {k:None for k in [2032,58,59,44,46,39,96,38,63,145,146,147,148,130,146,147,148,130,8242]}
#========== FUNCTIONS ========== 
# a function to search WorldCat for books
def process_books(row):
    ''' (str,str) -> str
    take a list of authors and a publication title, output a worldcat search opensearch query with combined authors and title
    '''
    failed = 0
    worked = 0
    query_base_URL = 'https://www.worldcat.org/search?q='
    book_URL_constant = '&fq=+(x0:book-+OR+(x0:book+x4:printbook)+-((x0:book+x4:digital))+-((x0:book+x4:mic))+-((x0:book+x4:thsis))+-((x0:book+x4:mss))+-((x0:book+x4:braille))+-((x0:book+x4:continuing)))'
    pub_int = row['year']
    pub_date = str(pub_int)
    title = row['name']
    # remove punctuation
    pub_title = title.translate(punctuation_dict)
    title_shortened = ' '.join(pub_title.split()[:5])
    short_title = str(title_shortened)
    #create a combined list of authors by surname
    authors = []
    for auth in ['a1','a2','a3','a4','a5','a6']:
        try:
            auth_surname = row[auth].split(',')[0].strip()
        except AttributeError:
            auth_surname = None
        if auth_surname != None:
           authors.append(auth_surname)
    author_list = "+au:".join(authors)
    title_date_query_URL = query_base_URL + 'ti:' + pub_title + book_URL_constant + '+yr:' + pub_date
    author_title_query_URL =  query_base_URL + 'ti:' + pub_title + author_list + book_URL_constant
    short_title_date_query_URL = query_base_URL + 'ti:' + short_title + book_URL_constant + '+yr:' + pub_date
    short_title_author_query = query_base_URL + 'ti:' + short_title + author_list + book_URL_constant
    '''
    print(query_URL)
    '''
    query_list = [title_date_query_URL, author_title_query_URL, short_title_date_query_URL, short_title_author_query]
    OCLC_list = []
    i = 0
    while len(OCLC_list) < 1 and i <= 3:
        query_URL = query_list[i]
        results_page =  requests.get(query_URL)
        page_soup = BeautifulSoup(results_page.content, 'html.parser')
        table_soup = page_soup.find("table",{"class": "table-results"})
        if table_soup:
            results_table = table_soup.find_all("div", class_="oclc_number")
            for row in results_table:
                OCLC_list.append(row.text)
        else:
            try_number = str(i)
        i = i + 1
    if len(OCLC_list) > 0:
        number_of_attempts =  str(i)
        number_of_OCLCs = str(len(OCLC_list))
        worked += worked
        print("Another success, moving on.")
    else:
        failed += failed
        "Failed, but moving on."
    
    
    
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

