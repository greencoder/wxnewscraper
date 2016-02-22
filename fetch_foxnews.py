import arrow
import bs4
import hashlib
import peewee
import requests
import sys

from models import NewsItem

source_url = 'http://www.foxnews.com/weather/index.html'
request = requests.get(source_url)
soup = bs4.BeautifulSoup(request.text, 'html.parser')

li_els = soup.findAll('li', class_='dv-item article-ct')

for li_el in li_els:

    headline = li_el.h3.text.strip()
    description = li_els[0].find('meta', {'itemprop': 'description'})['content'].strip()
    author = '' # No Author Info for this Feed
    link = li_el.h3.a['href'].strip()
    date = li_el.find('meta', {'itemprop': 'datePublished'})['content']

    # Make sure the link is absolute
    if not link.startswith('http'):
        link = 'https://www.foxnews.com' + link

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
    
    item.url_hash = url_hash
    item.title = headline
    item.authors = author
    item.summary = description
    item.source = "Fox News"
    item.link = link
    item.published_ts = arrow.get(date).timestamp
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()
    