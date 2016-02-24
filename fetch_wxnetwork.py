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

url  = 'http://appframework.pelmorex.com/api/appframework/Data/getData/iPhone?location=USCO0574'
url += '&dataType=News&deviceLang=en-US&appVersion=3.6.0.799&configVersion=38&resourceVersion=0&resourceCommonVersion=0'
request = requests.get(url)
data = request.json()
stories = data['News']['array']

for story_dict in stories:

    # Create a hash from the URL to make a unique identifier
    link = story_dict['WebLinks']['ShareLink']['Url']
    url_hash = hashlib.md5(link).hexdigest()

    # See if the item already exists
    try:
        item = NewsItem.get(NewsItem.url_hash==url_hash)
        print 'Item Exists. Skipping.'
        continue
    except peewee.DoesNotExist:
        print 'Creating new item.'
        item = NewsItem()

    # The date string says GMT, but doesn't agree with the date provided. 
    # We need to figure out the current offset and apply that first.
    date_string = story_dict['Timestamp']['GMT']
    offset = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime('%z')
    date_eastern = arrow.get(date_string + offset).to('US/Eastern')
    date_utc = date_eastern.to('UTC')
    published_date = date_eastern.format('YYYY-MM-DD')
    published_ts = date_utc.timestamp

    headline = story_dict['Title']['Text'][0]
    summary = story_dict['IntroText']['Text'][0]

    item.link = link 
    item.url_hash = url_hash
    item.title = headline
    item.summary = summary
    item.source = 'The Weather Network'
    item.published_date = published_date
    item.published_ts = published_ts
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()
