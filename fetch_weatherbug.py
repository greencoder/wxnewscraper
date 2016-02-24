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

source_url = 'http://weather.weatherbug.com/news/aurora-co-80017'
api_url = 'http://weather.weatherbug.com/api/media/stories?category=Featured&count=14'

# The API request relies on a cookie, so we have to first call the news URL so 
# that cookie gets set correctly. After that, we can successfully call the API.
session = requests.Session()
session.get(source_url)
api_request = session.get(api_url)
data = api_request.json()

for story_dict in data:

    link = 'http://weather.weatherbug.com' + story_dict['Url']
    
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

    date_string = story_dict['PublishDate']
    date_utc = arrow.get(date_string).to('UTC')
    date_eastern = date_utc.to('US/Eastern')
    published_date = date_eastern.format('YYYY-MM-DD')
    published_ts = date_utc.timestamp

    headline = story_dict['Title']
    summary = story_dict['Summary']

    item.link = link 
    item.url_hash = url_hash
    item.title = headline
    item.summary = summary
    item.source = 'WeatherBug'
    item.published_date = published_date
    item.published_ts = published_ts
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()
