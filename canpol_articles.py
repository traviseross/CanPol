#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ========== LIBRARIES ==========
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import json
import time

# this little dictionary strips unwelcome punctuation from titles for use in the searches
punctuation_dict = {
    k: None
    for k in [
        2032,
        58,
        59,
        44,
        46,
        39,
        96,
        38,
        63,
        145,
        146,
        147,
        148,
        130,
        146,
        147,
        148,
        130,
        8242,
    ]
}
global worldcat_query_base_URL
worldcat_query_base_URL = "https://www.worldcat.org"
global book_URL_constant
book_URL_constant = "&fq=+(x0:book-+OR+(x0:book+x4:printbook)+-((x0:book+x4:digital))+-((x0:book+x4:mic))+-((x0:book+x4:thsis))+-((x0:book+x4:mss))+-((x0:book+x4:braille))+-((x0:book+x4:continuing)))"
global RESTful_book_constant
RESTful_book_constant = "?editions#%2528x0%253Abook%2Bx4%253Aprintbook%2529format"
# ========== FUNCTIONS ==========
# def process_articles(query_list):
# a function to handle articles
#    pass

# def process_books(query_list):


# ========== MAIN ==========
# open the data from excel, store it in a dataframe
ps_data = pd.DataFrame()
output_data = pd.DataFrame()
full_data = pd.read_excel("/Users/travisross/travisross/Data/PS_Data.xlsx")
# iterate through each row, run the appropriate function per publication type
with open("Users/travisross/travisross/Data/standalone_articles.json", "w") as outfile:
    json.dump({}, outfile)
limit = 9000
for ID, row in full_data.iterrows():
    if row["ID"] == limit:
        break
    pub_type = int(row["pub_type"])
    # get publication date as a string
    pub_date = str(row["year"])
    # get title, then remove punctuation and create short and long variants
    title = row["name"]
    pub_title = title.translate(punctuation_dict)
    short_title = " ".join(pub_title.split()[:5])
    # get all the authors, but keep only the surnames in a list we can join with the appropriate operators later
    authors = []
    for auth in ["a1", "a2", "a3", "a4", "a5", "a6"]:
        try:
            auth_surname = row[auth].split(",")[0].strip()
        except AttributeError:
            auth_surname = None
        if auth_surname != None:
            authors.append(auth_surname)
    if pub_type == 1:
        if len(authors) > 0:
            auth_list = authors
            author_string = "&query.author=".join(auth_list)
        article_json = requests.get(
            "https://api.crossref.org/works?query.author="
            + author_string
            + "&query.bibliographic="
            + pub_title
            + "%20"
            + pub_date
            + "&rows=1"
        )
        article_info = json.loads(article_json.text)
        if article_info["status"] == "ok":
            try:
                print("Adding row " + str(row["ID"]))
                UUID = article_info["message"]["items"][0]["DOI"]
                with open(
                    "Users/travisross/travisross/Data/standalone_articles.json",
                    mode="a",
                ) as f:
                    json.dump(article_info, f)
            except IndexError:
                try:
                    print("Trying a different way for row " + str(row["ID"]))
                    article_json = requests.get(
                        "https://api.crossref.org/works?query.bibliographic="
                        + short_title
                        + "%20"
                        + pub_date
                        + "&rows=1"
                    )
                    article_info = json.loads(article_json.text)
                    if article_info["status"] == "ok":
                        try:
                            UUID = article_info["message"]["items"][0]["DOI"]
                            with open(
                                "Users/travisross/travisross/Data/articles.json", "w"
                            ) as outfile:
                                json.dump(article_info, outfile)
                        except IndexError:
                            pass
                except IndexError:
                    print("Something went wrong with " + pub_title + ".")
                    pass
