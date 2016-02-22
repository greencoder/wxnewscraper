import arrow
import bs4
import hashlib
import peewee
import requests
import sys
import unidecode

from models import NewsItem

url  = 'https://dsx.weather.com/cms/v1/a/?api=00728e87-7005-4043-9050-c84d5e7d8ca6'
url += '&pg=0,25'
#url += '&q=type:$in(%27article%27);tags.keyword:$in(%27TopStory%27)'
url += '&q=type:$in(%27article%27)'
url += '&sort=-lastmodifieddate'

request = requests.get(url)
data = request.json()

for entry in data:

    # Make sure the link is absolute
    link = entry['url']

    if not link.startswith('http'):
        link = 'https://www.weather.com' + link

    # Create a unique identifier from the hash of the URL
    url_hash = hashlib.md5(link).hexdigest()
    
    # See if the story already exists
    try:
        item = NewsItem.get(NewsItem.url_hash==url_hash)
        print 'Item Exists. Skipping.'
        continue
    except peewee.DoesNotExist:
        print 'Creating new item.'
        item = NewsItem()
    
    date = arrow.get(entry['publishdate'])
    dt = date.to('US/Eastern')
    published_ts = dt.timestamp
    published_date = dt.date().strftime('%Y-%m-%d')
    
    item.url_hash = url_hash
    item.title = unidecode.unidecode(entry['title'].strip())
    item.summary = unidecode.unidecode(entry['description'].strip())
    item.source = "Weather Channel"
    item.link = link
    item.published_date = published_date
    item.published_ts = published_ts
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()
