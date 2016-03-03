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
    
    date = arrow.get(entry['publishdate'])
    dt = date.to('US/Eastern')
    published_ts = dt.timestamp
    published_date = dt.date().strftime('%Y-%m-%d')

    pcollid = entry['pcollid']

    if entry['tags']:
        tags = entry['tags']['keyword']
    else:
        tags = []

    # Skip non weather.com stories
    if entry['providername'] != 'weather.com':
        print 'Skipping non weather.com story: %s' % entry['providername']
        continue

    # Skip lame stories
    
    skippable_collection_ids = (
        'health/allergy',
        'photos/places',
        'tv/shows/responding-by-storm',
        'travel',
    )
    
    # See if any of the skippable ids are in the story ids
    if pcollid in skippable_collection_ids:
        print 'Skipping %s story' % pcollid
        continue

    # If it's also published on weather underground, skip it
    if 'wunderground' in tags:
        print 'Skipping Weather Underground Story'
        continue

    # See if the story already exists
    try:
        item = NewsItem.get(NewsItem.url_hash==url_hash)
        print 'Item Exists. Skipping.'
        continue
    except peewee.DoesNotExist:
        print 'Creating new item.'
        item = NewsItem()

    item.url_hash = url_hash
    item.title = unidecode.unidecode(entry['title'].strip())
    item.summary = unidecode.unidecode(entry['description'].strip())
    item.source = "Weather Channel"
    item.link = link
    item.published_date = published_date
    item.published_ts = published_ts
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()
