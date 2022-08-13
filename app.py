#!/usr/bin/env python
from secrets import choice
from urllib import request
import random
import requests
import urllib
import time
from datetime import date
import sys
import re
import json
from flask_wtf import FlaskForm
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

class Film:
    def __init__(self, name, year):
        self.name = name
        self.year = year

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

def get_posters(page):
    filmList = []
    if page.ready == False:
        page.Load();
    # read posters
    posterContainer = page.soup.find(class_='poster-list')
    if posterContainer:
    #<img alt="John Wick: Chapter 2" class="image" height="105" src="https://s1.ltrbxd.com/static/img/empty-poster-70.84a.png" width="70"/>
        nameList = posterContainer.find_all('img')
        for film in range(0, len(nameList)):
            nameEntry = nameList[film]
            name = nameEntry.get('alt')
            name.encode('utf8')
            year = page.year;
            filmList.append(Film(name, year))
            # print('filmList: '+name)
    return filmList

# choose item in list
def chooseRandomItem(liste):
    itemNo = random.randint(0,len(liste)-1)
    return itemNo

# get last page number from page
def getListLastPage(page):
    pageDiscoveryList = page.soup.find_all('li', class_='paginate-page')
    pageCount = pageDiscoveryList[len(pageDiscoveryList)-1].a.get_text() # get last page
    return int(pageCount)

# build url
def buildUrl(film_name):
    return f'https://letterboxd.com/film/{strEncoder(film_name)}/'

# encode film name
def strEncoder(x):
    x = x.replace(" ", "-")
    for _ in [".",",",":","'","?","!","&"]: x = x.replace(_, "")
    return x.lower()

# choose a random film
def chooseFilm(film_list, num):
    film = film_list[num]
    filmName = str(film.name)
    return filmName

@app.route("/handle_data", methods =['GET', 'POST'])
def handle_data():

    if request.method == 'POST':
        urls = []
        for key, val in request.form.items():
            if key.startswith("url"):
                if val:
                    urls.append(val)

        randomList = random.randint(0,len(urls)-1) # make random number
        listUrl = urls[randomList] #choose random list

        pageList = []
        filmList = []

        class Page():
            def __init__(self, url, num):
                self.url = url
                self.num = num
                self.page = None
                self.soup = None
                self.year = 0
                self.ready = False
            def Load(self):
                self.page = requests.get(self.url)
                self.soup = BeautifulSoup(self.page.text,'html.parser')
                self.ready = True

        class Film():
            def __init__(self, name, rating, year):
                self.name = name
                self.rating = rating
                self.year = year

        # Find needed pages
        firstPage = Page(listUrl, 1)
        firstPage.Load()
        pageList.append(firstPage)
        lastPage = getListLastPage(firstPage)

        if lastPage == 0: # if there is only one page
            filmList = get_posters(pageList[0])
        else: # If more than 1 page exists
            for pageNum in range(2, lastPage + 1): # add range to search list
                pageTemp = Page(f'{listUrl}/page/{str(pageNum)}/', str(pageNum))
                pageList.append(pageTemp)

            # choose a random page
            pageNo = chooseRandomItem(pageList)
            filmList = get_posters(pageList[pageNo])

        filmNo = chooseRandomItem(filmList)
        filmName = chooseFilm(filmList, filmNo)
        filmLink = buildUrl(filmName)

        print(f'[{listUrl}]][{str(pageNo)}][{str(filmNo)}]: {filmName}')
        return render_template('home.html', link= filmLink, name = filmName)

if __name__ == '__main__': # if script is run directly
    app.run(debug=True) # run app in debug mode