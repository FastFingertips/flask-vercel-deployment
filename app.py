#!/usr/bin/env python
import random
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

class Film:
    def __init__(self, name, year):
        self.name = name
        self.year = year

@app.route("/")
@app.route("/home")
def home(): return render_template('home.html')

def getPosters(page): # get posters from page
    if page.ready == False: page.Load() # load page if not loaded
    posterContainer = page.soup.find(class_='poster-list') # read posters
    if posterContainer: # <img alt="John Wick: Chapter 4" class="image">
        nameList = posterContainer.find_all('img')
        filmList = []
        for film in range(0, len(nameList)):
            nameEntry = nameList[film]
            name = nameEntry.get('alt')
            name.encode('utf8')
            year = page.year;
            filmList.append(Film(name, year))
    return filmList

def chooseRandomItemNo(items): return random.randint(0,len(items)-1)

def getListLastPageNo(listObject): # get last page number from dom
    pageDiscoveryList = listObject.soup.find_all('li', class_='paginate-page')
    pageCount = 0
    try: pageCount = int(pageDiscoveryList[len(pageDiscoveryList)-1].a.get_text())
    except IndexError as e:
        print(e)
        try:
            metaDescription = listObject.soup.find('meta', attrs={'name':'description'}).attrs['content']
            filmCounts = int(metaDescription[metaDescription.find('A list of')+9:metaDescription.find('films')].strip().replace(',',''))
            if filmCounts < 101: pageCount = 1
            if filmCounts > 100: pageCount = int(pageCount/100) + (0 if pageCount % 100 == 0 else 1)
        except Exception as e: print(e)
    except Exception as e: print(e)
    if pageCount: return pageCount
    else: exit()

def strEncoder(x): # encode string for url
    x = x.replace(" ", "-")
    for _ in [".",",",":","'","?","!","&"]: x = x.replace(_, "")
    return x.lower()

def buildUrl(film_name): return f'https://letterboxd.com/film/{strEncoder(film_name)}/'

def chooseItem(itemList, itemNo): # choose a random film
    item = itemList[itemNo]
    itemName = str(item.name)
    return itemName

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
        filmName = chooseItem(filmList, filmNo)
        filmLink = buildUrl(filmName)

        print(f'[{listUrl}]][{str(pageNo)}][{str(filmNo)}]: {filmName}')
        return render_template('home.html', link= filmLink, name = filmName)

if __name__ == '__main__': # if script is run directly
    app.run(debug=True) # run app in debug mode