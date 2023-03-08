#import the libraries
import os
import time

import numpy as np
import pandas as pd
import math
import time
import re
import httpx
import json

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen


def main():
    company_name = input("Enter Brand: ")
    page_specify = input("Pages To Scrape (Input 0 if you want to scrape all pages): ") #this will give you an option Specify how many pages you'd like to scrape, if you don't want to specify just input 0
    def find_companies(query: str):
        result = httpx.get(
                  url=f"https://www.glassdoor.com/searchsuggest/typeahead?numSuggestions=8&source=GD_V2&version=NEW&rf=full&fallback=token&input={query}",
                  )
        data = json.loads(result.content)
        return data[0]["suggestion"], data[0]["employerId"]

    #define main variables
    company_name = find_companies(str(company_name))[0]
    #company_name_format = company_name.replace(" ", "-") #this will be used when requesting data
    company_id = find_companies(str(company_name))[1]

    #this will look at the input and if it has more than 1 word it will add a hypen between it
    words = company_name.split()
    if len(words) > 1:
        company_name_format = '-'.join(words)
    else:
        company_name_format = company_name

    url_fetch = f'https://www.glassdoor.co.uk/Reviews/{company_name_format}-Reviews-E{company_id}'+'_P'+str(1)+'.htm?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng'

    #f'https://www.glassdoor.co.uk/Reviews/{company_name_format}-Reviews-E{company_id}'+'_P'+str(1)+'.htm?filter.iso3Language=eng'

    def basic_info():
        url = url_fetch
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
        req = Request(url,headers=hdr)
        page = urlopen(req)
        status_code = page.getcode()
        soup = BeautifulSoup(page, "html.parser")
        print(status_code)


        #check the total number of reviews
        countReviews = soup.find('div', {'data-test':'pagination-footer-text'}).text
        countReviews = float(countReviews.split(' Reviews')[0].split('of ')[1].replace(',',''))

        #calculate the max number of pages (assuming 10 reviews a page)
        countPages = math.ceil(countReviews/10) + 1

        return countReviews, countPages


    #This will run an if statement, where if input is 0 it will output all pages, if you specify pages then it will scrape only those pages
    pages = 0
    if int(page_specify) > 0:
        pages = int(page_specify) + 1
    else:
        pages = basic_info()[1] #this will scrape all pages

    #We then create a start and end point to scrape pages, by default we will start on page 1 and scrape
    start = 1
    end = pages                  #basic_info()[1] # you can change this and update when needed
    step = 1
    page_number = range(start, end, step)

    #define empty strings
    Summary=[]
    Date_n_JobTitle=[]
    Date=[]
    JobTitle = []
    AuthorLocation = []
    OverallRating = []
    Pros = []
    Cons = []


    #The following for loop will need to be reviewed to make sure the HTML code is still constant and make tweaks as necessary
    for i in page_number:
        # Old f'https://www.glassdoor.co.uk/Reviews/{company_name_format}-Reviews-E{company_id}'+'_P'+str(i)+'.htm?filter.iso3Language=eng'
        url = f'https://www.glassdoor.co.uk/Reviews/{company_name_format}-Reviews-E{company_id}'+'_P'+str(i)+'.htm?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng'
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
        req = Request(url,headers=hdr)
        page = urlopen(req)
        status_code = page.getcode()
        soup = BeautifulSoup(page, "html.parser")
        print(status_code)
        print(url)

        for x in soup.find_all('a', {'class':'reviewLink'}):
            Summary.append(x.text)

        #get the Posted Date and Job Title
        for x in soup.find_all('span', {'class':'middle common__EiReviewDetailsStyle__newGrey'}):
            Date_n_JobTitle.append(x.text)

        #get the Posted Date
        for x in Date_n_JobTitle:
            Date.append(x.split(' -')[0])

        #get Job Title
        for x in Date_n_JobTitle:
            JobTitle.append(x.split(' -')[1])

      #Author Location
        for x in soup.find_all('span', {'class': 'middle'}):
            second_span = x.find('span')
            if second_span is not None:
                AuthorLocation.append(second_span.get_text(strip=True))

              #get Overall Rating
        for x in soup.find_all('span', {'class':'ratingNumber mr-xsm'}):
            OverallRating.append(float(x.text))

            #get Pros
        for x in soup.find_all('span', {'data-test':'pros'}):
            Pros.append(x.text)

       #get Cons
        for x in soup.find_all('span', {'data-test':'cons'}):
            Cons.append(x.text)


        time.sleep(10)

    Reviews_1 = pd.DataFrame(list(zip(Summary, Date, JobTitle, AuthorLocation, OverallRating, Pros, Cons)),
                columns = ['Summary', 'Date', 'JobTitle', 'AuthorLocation', 'OverallRating', 'Pros', 'Cons'])

    Reviews_1.to_excel(f'{company_name}.xlsx')

if __name__ == "__main__":
    main()
