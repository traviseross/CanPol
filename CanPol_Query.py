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
with open("Users/travisross/travisross/Data/articles.json", "w") as outfile:
    json.dump({}, outfile)
# iterate through each row, run the appropriate function per publication type
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
    original_row = {
        "ID": row["ID"],
        "department": row["department"],
        "a1": row["a1"],
        "a2": row["a2"],
        "a3": row["a3"],
        "a4": row["a4"],
        "a5": row["a5"],
        "a6": row["a6"],
        "g1": row["g1"],
        "g2": row["g2"],
        "g3": row["g3"],
        "g4": row["g4"],
        "g5": row["g5"],
        "g6": row["g6"],
        "year": row["year"],
        "pub_type": row["pub_type"],
        "name": row["name"],
        "publisher_country": row["publisher_country"],
        "singlen_comparative": row["singlen_comparative"],
        "quant_qual": row["quant_qual"],
        "language": row["language"],
        "sorted_section": row["sorted_section"],
    }
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
                UUID = article_info["message"]["items"][0]["DOI"]
                with open(
                    "Users/travisross/travisross/Data/standalone_articles.json",
                    mode="a",
                ) as f:
                    json.dump(article_info, f)
            except IndexError:
                try:
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
                                "Users/travisross/travisross/Data/standalone_articles.json",
                                mode="a",
                            ) as f:
                                json.dump(article_info, f)
                        except IndexError:
                            pass
                except IndexError:
                    print("Something went wrong with " + pub_title + ".")
                    pass
    else:
        OCLC_final = ""
        if len(authors) > 0:
            auth_list = authors
            author_string = "+au:".join(auth_list)
        query_list = [
            worldcat_query_base_URL + "/title/" + pub_title + RESTful_book_constant,
            worldcat_query_base_URL
            + "/search?q="
            + "ti:"
            + pub_title
            + book_URL_constant
            + "+yr:"
            + pub_date,
            worldcat_query_base_URL
            + "/search?q="
            + "ti:"
            + short_title
            + "+au:"
            + author_string
            + book_URL_constant,
            worldcat_query_base_URL
            + "/search?q="
            + "ti:"
            + short_title
            + book_URL_constant
            + "+yr:"
            + pub_date,
            worldcat_query_base_URL
            + "/search?q="
            + "ti:"
            + short_title
            + "+au:"
            + author_string
            + book_URL_constant,
        ]
        OCLC_list = []
        for query_URL in query_list:
            if OCLC_final != "":
                UUID = OCLC_final
                break
            else:
                results_page = requests.get(query_URL)
                page_soup = BeautifulSoup(results_page.content, "html.parser")
                table_soup = page_soup.find("table", {"class": "table-results"})
                if table_soup:
                    by_title_table_soup = table_soup.find_all(
                        "tr", {"class": "menuElem"}
                    )
                    if by_title_table_soup:
                        for by_title_candidate in by_title_table_soup:
                            item_type_tag = by_title_candidate.find_all(
                                "span", {"class": "itemType"}
                            )
                            for item in item_type_tag:
                                if item.text == "Print book":
                                    candidate_oclc = by_title_candidate.find_all(
                                        "div", {"class": "oclc_number"}
                                    )
                                    for candidate in candidate_oclc:
                                        candidate_oclc = candidate.text
                                        OCLC_list.append(candidate_oclc)
                                        OCLC_list = list(set(OCLC_list))
                                        if len(OCLC_list) > 0:
                                            OCLC_final = OCLC_list[0]
    new_ps_row = {
        "department": original_row["department"],
        "a1": original_row["a1"],
        "a2": original_row["a2"],
        "a3": original_row["a3"],
        "a4": original_row["a4"],
        "a5": original_row["a5"],
        "a6": original_row["a6"],
        "g1": original_row["g1"],
        "g2": original_row["g2"],
        "g3": original_row["g3"],
        "g4": original_row["g4"],
        "g5": original_row["g5"],
        "g6": original_row["g6"],
        "year": original_row["year"],
        "pub_type": original_row["pub_type"],
        "name": original_row["name"],
        "publisher_country": original_row["publisher_country"],
        "singlen_comparative": original_row["singlen_comparative"],
        "quant_qual": original_row["quant_qual"],
        "language": original_row["language"],
        "sorted_section": original_row["sorted_section"],
        "UUID": str(UUID),
    }
    ps_data = ps_data.append(new_ps_row, ignore_index=True)
    row_data = {"key": str(UUID), "pub_title": pub_title, "ID": [ID]}
    if str(UUID) in output_data.values:
        row_idx = output_data[output_data["key"] == UUID].index[0]
        output_data.iloc[row_idx]["ID"] += row_data["ID"]
        print("already had row " + str(ID) + " by UUID")
    elif pub_title in output_data.values:
        row_idx = output_data[output_data["pub_title"] == pub_title].index[0]
        output_data.iloc[row_idx]["ID"] += row_data["ID"]
        print("already had row " + str(ID) + " by title")
    else:
        output_data = output_data.append(row_data, ignore_index=True)
        print("row " + str(ID) + " was added new")
output_data.to_csv("~/travisross/CanPol/CanPol_Data.tsv", sep="\t")
ps_data.to_csv("~/travisross/CanPol/PS_Data.tsv", sep="\t")
