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

source_url = 'http://www.sandiegouniontribune.com/news/weather/'
request = requests.get(source_url)
soup = bs4.BeautifulSoup(request.text, 'html.parser')
article_els = soup.findAll('article', class_='story_list span3 col')

for article_el in article_els:

    div_el = article_el.find('div', class_='content')

    link = 'http://www.sandiegouniontribune.com/news/weather/' + div_el.a['href']
    
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

    date = div_el.find('p', class_='date').text.replace('Updated', '').strip()
    dt = dateutil.parser.parse(date)
    dt = dt.replace(tzinfo=pytz.timezone('US/Pacific'))
    published_date = arrow.get(dt).date().strftime('%Y-%m-%d')

    headline = div_el.a.text.strip()
    published_ts = arrow.get(dt).to('UTC').timestamp
    summary = ''

    item.link = link 
    item.url_hash = url_hash
    item.title = headline
    item.summary = summary
    item.source = 'San Diego Union Tribune'
    item.published_date = published_date
    item.published_ts = published_ts
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()


