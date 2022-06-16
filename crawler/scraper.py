#!/usr/bin/python
from time import time
from crawler import get_matches
from selenium import webdriver
from bs4 import BeautifulSoup
import re
from csv import writer
from datetime import date, timedelta
from selenium.webdriver.common.proxy import Proxy, ProxyType

sdate = date(2022,1,4)   # start date
edate = date(2022,6,9)   # end date

def dates_bwn_twodates(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'socksProxy': '127.0.0.1:9050',
    'socksVersion': 5,
})

def get_features(url):
    
    fire_options = webdriver.FirefoxOptions()

    #fire_options.headless = True
    fire_options.proxy = proxy
    fire_options.binary_location = '/home/adriel/Desktop/tor-browser_en-US/Browser/firefox'
    fire_options.headless = True
    driver = webdriver.Firefox(options=fire_options) # Could be any other browser you have the drivers for
    driver.get(url)
    html = driver.page_source
    code = str(BeautifulSoup(html, 'html.parser'))
    driver.close()

    start = code.find("Pitch: ")
    end = code[start:].find("</li>")

    pitch = code[start + 7:start+end].replace(" ", "")


    start = code.find("Weather: ")
    end = code[start:].find("</li>")

    weather = code[start + 9:start+end].replace(" ", "")

    s_start = code.find("Full Time")
    data = []
    for i in range(20):
        start2 = code[s_start:].find("<div class=\"small-2 text-center columns\">")+len("<div class=\"small-2 text-center columns\">")
        s_start += start2
        end = code[s_start:].find("</div>")

        data.append(code[s_start:s_start+end])

    start = code.find("Score After Full Time - ")
    end1 = code[start+len("Score After Full Time - "):].find("-")
    end2 = code[start+len("Score After Full Time - "):].find("</li>")

    score_home_f_time = code[start+len("Score After Full Time - "):start+len("Score After Full Time - ")+end1]
    score_away_f_time = code[start+len("Score After Full Time - ")+end1+1:start+len("Score After Full Time - ")+end2].replace(" ", "")

    start = code.find("Score After First Half - ")
    end1 = code[start+len("Score After First Half - "):].find("-")
    end2 = code[start+len("Score After First Half - "):].find("</li>")

    score_home_h_time = code[start+len("Score After First Half - "):start+len("Score After First Half - ")+end1]
    score_away_h_time = code[start+len("Score After First Half - ")+end1+1:start+len("Score After First Half - ")+end2].replace(" ", "")
    

    start = code.find("Live Scores of ")+len("Live Scores of ")
    end = code.find("vs")
    home = code[start:end].replace(" ", "")

    start = code.find("vs")+len("vs")

    end = code[start:].find("-")
    away = code[start:start+end].replace(" ", "")

    start = code.find("Score After Full Time - ")
    end = code.find("Score After First Half - ")
    corners_away = code[start:end].count("th Corner - "+away)+code[start:end].count("st Corner - "+away)+code[start:end].count("nd Corner - "+away)+code[start:end].count("rd Corner - "+away)
    corners_home = code[start:end].count("th Corner - "+home)+code[start:end].count("st Corner - "+home)+code[start:end].count("nd Corner - "+home)+code[start:end].count("rd Corner - "+home)


    start = code.find("Score After First Half - ")
    end = code.find("Pitch: ")
    corners_away_FH = code[start:end].count("th Corner - "+away)+code[start:end].count("st Corner - "+away)+code[start:end].count("nd Corner - "+away)+code[start:end].count("rd Corner - "+away)
    corners_home_FH = code[start:end].count("th Corner - "+home)+code[start:end].count("st Corner - "+home)+code[start:end].count("nd Corner - "+home)+code[start:end].count("rd Corner - "+home)

    start = code.find("Score After Full Time - ")
    end = code.find("Score After First Half - ")

    last_half = code[start:end]

    start = last_half.find("th Corner - ")
    if(start == -1):
        start = last_half.find("rd Corner - ")

    if(start == -1):
        start = last_half.find("nd Corner - ")

    if(start == -1):
        start = last_half.find("st Corner - ")
    
    end = last_half[start-10:].find("</li>")

    times = re.findall(r'\d+', last_half[start-10:start-10+end])
    times = [int(i) for i in times]

    target_last_half = any([i > 88 for i in times])


    start = code.find("Score After First Half - ")
    end = code.find("Pitch: ")

    last_half = code[start:end]

    start = last_half.find("th Corner - ")
    if(start == -1):
        start = last_half.find("rd Corner - ")

    if(start == -1):
        start = last_half.find("nd Corner - ")

    if(start == -1):
        start = last_half.find("st Corner - ")
    
    end = last_half[start-10:].find("</li>")

    times = re.findall(r'\d+', last_half[start-10:start-10+end])
    times = [int(i) for i in times]

    target_first_half = any([i > 39 for i in times])

    return ([pitch, weather, score_home_h_time, score_away_h_time, corners_home_FH, corners_away_FH, data[0], data[1],data[2], data[3],data[4], data[5], data[6], data[7], data[8], data[9], target_first_half],[pitch, weather, score_home_f_time, score_away_f_time, corners_home, corners_away, data[10], data[11],data[12], data[13],data[14], data[15], data[16], data[17], data[18], data[19], target_last_half])

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

def fill_table(list_dates):
    for date in list_dates:
        print("Actual date is: "+date)
        matches = get_matches(date)
        counter = 1
        for match in matches:
            print("line: "+str(counter))
            counter+=1
            list1, list2 = get_features("https://www.scorebing.com"+match)
            append_list_as_row("Dataset.csv", list1)
            append_list_as_row("Dataset.csv", list2)
        



dates = [str(d).replace("-", "") for d in dates_bwn_twodates(sdate,edate)]


fill_table(dates)