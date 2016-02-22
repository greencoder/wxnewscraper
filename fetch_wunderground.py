import arrow
import bs4
import datetime
import dateutil.parser
import hashlib
import peewee
import requests
import sys

from models import NewsItem

source_url = 'http://www.wunderground.com/news/'
request = requests.get(source_url)
soup = bs4.BeautifulSoup(request.text, 'html.parser')

h1_el = soup.find('h1', text='Weather Articles')
tr_els = h1_el.findAllNext('tr')

for tr_el in tr_els:
    
    # If there is no hyperlink, skip it
    if tr_el.a == None:
        continue
    
    # Make sure the URL is absolute
    link = tr_el.a['href'].strip()
    if not link.startswith('http'):
        link = 'http://www.wunderground.com' + link
    
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

    item.link = link 
    item.url_hash = url_hash
    item.title = tr_el.h3.text.strip()
    item.summary = tr_el.p.text.strip()
    item.source = 'Weather Underground'
    
    # The author and date are in the same text string
    parts = tr_el.em.text.strip().split('\n\t\t')
    
    if len(parts) == 1:
        item.authors = ''
        timestamp = arrow.get(dateutil.parser.parse(parts[0])).timestamp
        item.published_ts = timestamp
    else:
        item.authors = parts[0]
        timestamp = arrow.get(dateutil.parser.parse(parts[1])).timestamp
        item.published_ts = timestamp

    item.inserted_ts = arrow.utcnow().timestamp
    item.save()
