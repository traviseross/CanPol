#!/usr/bin/python3
# -*- coding: utf-8 -*-
#========== LIBRARIES ========== 
from bs4 import BeautifulSoup
import re
import pandas as pd
import requests

#========== FUNCTIONS =======p=== 
def parse_dissertations_page(page_text):
    #parse page with bs
    page_text_soup = BeautifulSoup(page_text,'html.parser')
    #get all dissertations within the table (regex class selection)
    dissertations = page_text_soup.find_all("tr",{"class":re.compile("[1-9]*_row")})
    #create list of dissertations in json-able format
    dissertations_json = []
    for dissertation in dissertations:
        dissertation_obj = dissertation.td
        #always found?
        #after first bold tag
        dissertator = dissertation_obj.find('b').next_sibling.string
        #requires a nested hyperlink after first bold tag
        department = dissertation_obj.find_all('b')[1].next_sibling.next_sibling.string #dissertation_obj.find('b').next_sibling.next_sibling.find('a').string
        #requires a nested hyperlink after first bold tag and further bold tag nesting
        dissertation_title = dissertation_obj.find_all('b')[2].next_sibling.string #dissertation.find('b').next_sibling.next_sibling.find('b').next_sibling.next_sibling.next_sibling.find('b').next_sibling.string
        #check for advisor
        try:
            advisor = dissertation_obj.find('span',{"id":re.compile("[0-9]*adv_box")}).text.split(":")[1].strip()
        except IndexError:
            advisor = ""
        try:
            status = dissertation_obj.find('span',{"id":re.compile("[0-9]*\_status")})
            scripts = page_text_soup.find_all("script")
            #first script object in the page soup containing id match (via re.search)
            script_id = list(filter(re.compile(status['id']).search,[s.text for s in scripts]))[0]
            #KLUDGE get text of first line which contains status['id'] of the format "\t$('#STATUS_ID').text('DISSERTATION');"
            status_val = re.sub("[\(\)\'\;]","",[l for l in script_id.split("\r\n") if l.find(status["id"])!=-1][0].split("text")[1])
        except IndexError:
            status = ""
        #save dictionary, append to list of dissertations
        dissertation_json = { "Dissertator":dissertator, "Department":department, "Dissertation Title":dissertation_title, "Advisor":advisor, "Completion":status_val}
        dissertations_json.append(dissertation_json)
    #return list of dissertations in json-able format
    return(dissertations_json)

#========== MAIN ========== 
#post request dissertations search
search_params = {
"Referrer":"https://secure.historians.org/members/services/cgi-bin/memberdll.dll/info?wrp=dissertations.htm",
"DNT":1,
"AWARDSTT":"Awarded",
"YRFILTER":">",
"YEAR":"2000",
"QNAME":"SEARCHDISS",
"WHP":"SearchDiss_h.htm",
"WBP":"SearchDiss.htm",
"WNR":"SearchDiss_norec.htm",
"RANGE":"1/20",
"AWARDNAME":"DISSERTATIONS",
"n":"~",
#l 
#"e":""
#"AWARDDESC":""
"AWARDDATE":">2000",
"SORT":"OWNERNAME,AWARDDATE,RELATIONSHIPTYPE"
}
search_uri = "https://secure.historians.org/members/services/cgi-bin/utilities.dll/customlist"
#get result of search
r = requests.post(search_uri,data=search_params)
#parse initial search result page
r_soup = BeautifulSoup(r.text,'html.parser')
#get number of records obtained by the search
recordcnt = r_soup.find("span",{"class":"recordCnt"})
recordcnt_int = int(recordcnt.text)

dissertations = []
#compute range values 
for range_val in range(1,recordcnt_int,20):
    iterate_params = search_params
    iterate_params["RANGE"] = "{}/20".format(range_val)
    try:
        r = requests.get(search_uri,iterate_params)
    except :
        r = requests.get(search_uri,iterate_params)
    print("Parsing results {} to {} of {}".format(range_val,range_val+19,recordcnt_int)) 
    d = parse_dissertations_page(r.text)
    dissertations+=d
#write to csv
dissertations_df = pd.DataFrame(dissertations)
dissertations_df.to_csv("/tmp/dissertations.csv")
