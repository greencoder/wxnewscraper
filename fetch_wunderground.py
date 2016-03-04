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

from models import NewsItem

source_url = 'http://www.wunderground.com/news/'
request = requests.get(source_url)
soup = bs4.BeautifulSoup(request.text, 'html.parser')

h1_el = soup.find('h1', text='Weather Articles')
tr_els = h1_el.findAllNext('tr')

for tr_el in tr_els:
    
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

    summary = tr_el.p.text.strip()
    headline = tr_el.h3.text.strip()

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

    if headline.endswith(' - wunderground.com'):
        headline = headline.replace(' - wunderground.com', '')

    item.link = link 
    item.url_hash = url_hash
    item.title = headline
    item.summary = summary
    item.source = 'Weather Underground'
    
    # The author and date are in the same text string
    parts = tr_el.em.text.strip().split('\n\t\t')
    
    if len(parts) == 1:
        dt = dateutil.parser.parse(parts[0])
        dt = dt.replace(tzinfo=pytz.timezone('US/Eastern')).strftime('%Y-%m-%d') + 'T00:00:00-05:00'
        timestamp = arrow.get(dt).to('UTC').timestamp
        published_date = arrow.get(dt).date().strftime('%Y-%m-%d')
        item.published_ts = timestamp
    else:
        dt = dateutil.parser.parse(parts[1])
        dt = dt.replace(tzinfo=pytz.timezone('US/Eastern')).strftime('%Y-%m-%d') + 'T00:00:00-05:00'
        timestamp = arrow.get(dt).to('UTC').timestamp
        published_date = arrow.get(dt).date().strftime('%Y-%m-%d')
        item.published_ts = timestamp

    # Stories are posted without times, so we just assign the current time to the story
    # since we check every 30 minutes. It's better than showing every story as midnight
    item.published_ts = arrow.utcnow().timestamp

    item.published_date = published_date
    item.inserted_ts = arrow.utcnow().timestamp
    item.save()
    
    # Sleep between requests
    time.sleep(1)
