#!/usr/bin/env python
import random
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

class Film:
    def __init__(self, name, url):
        self.name = name
        self.url = url

@app.route("/")
@app.route("/home")
def home(): return render_template('home.html')

def getPosters(page): # get posters from page
    if page.ready == False: page.Load() # load page if not loaded
    posterContainer = page.soup.find(class_='poster-list') # read posters
    if posterContainer: # <img alt="John Wick: Chapter 4" class="image">
        posterImgs = posterContainer.find_all('img')
        posterDivs = posterContainer.find_all('div')
        filmList = []
        for filmNo in range(len(posterImgs)):
            name = posterImgs[filmNo].attrs['alt']
            name.encode('utf-8')
            url = posterDivs[filmNo].attrs['data-target-link']
            filmList.append(Film(name, url))
    return filmList

def chooseRandomItemNo(items): return random.randint(0,len(items)-1)

def getListLastPageNo(listObject): # get last page number from dom
    pageCount = 1
    try: # try li tag
        pageDiscoveryList = listObject.soup.find_all('li', class_='paginate-page')
        pageCount = int(pageDiscoveryList[len(pageDiscoveryList)-1].a.get_text())
    except IndexError as e: # try meta tag
        metaDescription = listObject.soup.find('meta', attrs={'name':'description'}).attrs['content']
        filmCounts = int(metaDescription[metaDescription.find('A list of')+9:metaDescription.find('films')].strip().replace(',',''))
        if filmCounts < 101: pageCount = 1
        if filmCounts > 100: pageCount = int(pageCount/100) + (0 if pageCount % 100 == 0 else 1)
    return pageCount

def buildUrl(v): return f'https://letterboxd.com{v}'

def chooseItem(itemList, itemNo): # choose a random film
    item = itemList[itemNo]
    return item

@app.route("/handle_data", methods =['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        listUrls = []
        for key, val in request.form.items():
            if key.startswith("url"):
                if val: listUrls.append(val)

        class Page():
            def __init__(self, url, num):
                self.url = url
                self.num = num
                self.page = None
                self.soup = None
                self.ready = False
            def Load(self):
                self.page = requests.get(self.url)
                self.soup = BeautifulSoup(self.page.text,'html.parser')
                self.ready = True

        listUrl = listUrls[chooseRandomItemNo(listUrls)]
        firstPage = Page(listUrl, 1)
        firstPage.Load()

        pageList, filmList = [], []
        pageList.append(firstPage)
        lastPage = getListLastPageNo(firstPage) # get last page from first page

        if lastPage == 1: # if only one page
            pageNo = lastPage
            filmList = getPosters(pageList[0])
        else: # if there is more than one page
            for pageNum in range(2, lastPage + 1): # 2 to last page
                pageTemp = Page(f'{listUrl}/page/{str(pageNum)}/', pageNum)
                pageList.append(pageTemp)

            pageNo = chooseRandomItemNo(pageList) # choose random page
            filmList = getPosters(pageList[pageNo]) # get posters from page

        filmNo = chooseRandomItemNo(filmList)
        film = chooseItem(filmList, filmNo)
        filmName, filmLink = film.name, buildUrl(film.url)

        print(f'[{listUrl}]][{str(pageNo)}][{str(filmNo)}]: {filmName}')
        return render_template('home.html', link= filmLink, name = filmName)

if __name__ == '__main__': # if script is run directly
    app.run(debug=True) # run app in debug mode