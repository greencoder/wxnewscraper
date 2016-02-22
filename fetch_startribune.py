import arrow
import bs4
import datetime
import dateutil.parser
import hashlib
import peewee
import pytz
import requests
import sys
import unidecode

from models import NewsItem

source_url = 'http://www.startribune.com/weather/'
request = requests.get(source_url)
soup = bs4.BeautifulSoup(request.text, 'html.parser')
h3_el = soup.find('h3', text='Weather News')
div_els = h3_el.findAllNext('div', class_='tease')

for div_el in div_els:

    link = div_el.find('div', class_='tease-container-right').h3.a['href']
    
    # Create a hash from the URL to make a unique identifier
    url_hash = hashlib.md5(link).hexdigest()

    # See if the item already exists
    try:
        item = NewsItem.get(NewsItem.url_hash==url_hash)
        print 'Item Exists. Skipping.'
        continue
    except peewee.DoesNotExist:
        print 'Creating new item.'
        item = NewsItem()

    date = div_el.find('div', class_='tease-timestamp')['data-st-timestamp']
    published_ts = arrow.get(date).timestamp
    headline = div_el.find('div', class_='tease-container-right').h3.text.strip()
    summary = div_el.find('div', class_='tease-summary').text.strip()

    item.link = link 
    item.url_hash = url_hash
    item.title = headline
    item.summary = summary
    item.authors = ''
    item.source = 'StarTribune'
    item.published_ts = published_ts
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()