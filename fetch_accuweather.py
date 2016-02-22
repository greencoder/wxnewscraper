import arrow
import bs4
import dateutil.parser
import hashlib
import peewee
import pytz
import requests
import sys
import time

from models import NewsItem

source_url = 'http://www.accuweather.com/en/weather-news'
request = requests.get(source_url)
soup = bs4.BeautifulSoup(request.text, 'html.parser')

ul_els = soup.findAll('ul', class_='articles')

for ul_el in ul_els:
    
    li_el = ul_el.find('li')
    link = li_el.find('a')['href']
    headline = li_el.find('h4').text
    date = li_el.find('h5').text
    description = li_el.find('p').text
    
    # Parse the date
    dt = dateutil.parser.parse(date)
    dt = dt.replace(tzinfo=pytz.timezone('US/Eastern'))
    utc_dt = arrow.get(dt).to('UTC')
    published_date = arrow.get(dt).date().strftime('%Y-%m-%d')
    
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
        description = meta_og_desc_el['content'].strip()
        
    if meta_og_url_el is not None:
        link = meta_og_url_el['content']
    
    item.link = link
    item.url_hash = url_hash
    item.title = headline
    item.summary = description
    item.source = "Accuweather"
    item.published_date = published_date
    item.published_ts = utc_dt.timestamp
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()
    
    # Sleep between requests
    time.sleep(1)
