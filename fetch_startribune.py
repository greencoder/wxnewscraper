import arrow
import bs4
import datetime
import dateutil.parser
import hashlib
import peewee
import pytz
import requests
import sys
import time
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
    published_date = arrow.get(date).date().strftime('%Y-%m-%d')
    summary = div_el.find('div', class_='tease-summary').text.strip()
    headline = div_el.find('div', class_='tease-container-right').h3.text.strip()
    
    # Try to get the opengraph data
    try:
        link_request = requests.get(link)
        links_soup = bs4.BeautifulSoup(link_request.text, 'html.parser')
        meta_og_title_el = links_soup.find('meta', {'property': 'og:title'})
        meta_og_desc_el = links_soup.find('meta', {'property': 'og:description'})
        meta_og_url_el = links_soup.find('meta', {'property': 'og:url'})
    except Exception, e:
        meta_og_title_el = None
        meta_og_desc_el = None
        meta_og_url_el = None

    if meta_og_title_el is not None:
        headline = meta_og_title_el['content'].strip()

    if meta_og_desc_el is not None:
        summary = meta_og_desc_el['content'].strip()

    if meta_og_url_el is not None:
        link = meta_og_url_el['content']

    item.link = link 
    item.url_hash = url_hash
    item.title = headline
    item.summary = summary
    item.source = 'Star Tribune'
    item.published_date = published_date
    item.published_ts = published_ts
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()
    
    # Sleep between requests to be polite
    time.sleep(1)
