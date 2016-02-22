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

source_url = 'http://www.sandiegouniontribune.com/news/weather/'
request = requests.get(source_url)
soup = bs4.BeautifulSoup(request.text, 'html.parser')
article_els = soup.findAll('article', class_='story_list span3 col')

for article_el in article_els:

    div_el = article_el.find('div', class_='content')

    link = 'http://www.sandiegouniontribune.com' + div_el.a['href']
    
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

    # Try to get the opengraph data
    try:
        link_request = requests.get(link)
        links_soup = bs4.BeautifulSoup(link_request.text, 'html.parser')
        meta_og_title_el = links_soup.find('meta', {'property': 'og:title'})
        meta_og_desc_el = links_soup.find('meta', {'property': 'og:description'})
        meta_og_url_el = links_soup.find('meta', {'property': 'og:url'})
        meta_published_el = links_soup.find('meta', {'itemprop': 'datePublished'})
    except Exception, e:
        meta_og_title_el = None
        meta_og_desc_el = None
        meta_og_url_el = None
        meta_published_el = None

    if meta_og_title_el is not None:
        headline = meta_og_title_el['content'].strip()

    if meta_og_desc_el is not None:
        summary = meta_og_desc_el['content'].strip()

    if meta_og_url_el is not None:
        link = meta_og_url_el['content']

    if meta_published_el is not None:
        published_datetime = meta_published_el['content']
        dt = arrow.get(published_datetime).datetime
        dt = dt.replace(tzinfo=pytz.timezone('US/Pacific'))
        published_ts = arrow.get(dt).to('UTC').timestamp
        published_date = arrow.get(dt).datetime.strftime('%Y-%m-%d')

    item.link = link 
    item.url_hash = url_hash
    item.title = headline
    item.summary = summary
    item.source = 'San Diego Union Tribune'
    item.published_date = published_date
    item.published_ts = published_ts
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()

    # Sleep between requests
    time.sleep(1)

