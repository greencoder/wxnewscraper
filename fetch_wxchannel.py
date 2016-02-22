import arrow
import bs4
import hashlib
import peewee
import requests
import sys

from models import NewsItem

url  = 'https://dsx.weather.com/cms/v1/a/?api=00728e87-7005-4043-9050-c84d5e7d8ca6'
url += '&pg=0,50'
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
    
    item.url_hash = url_hash
    item.title = entry['title']
    item.authors = ", ".join(entry['author'])
    item.summary = entry['description']
    item.source = "Weather Channel"
    item.link = link
    item.published_ts = arrow.get(entry['publishdate']).timestamp
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()
    
# u'source_name',
# u'teaserTitle',
# u'locale',
# u'lastmodifieddate',
# u'publishdate',
# u'id',
# u'wxnodes',
# u'source_guid',
# u'title',
# u'schema_version',
# u'adsmetrics',
# u'seometa',
# u'type',
# u'body',
# u'description',
# u'providername',
# u'tags',
# u'createdate',
# u'providerid',
# u'variants',
# u'url',
# u'author',
# u'pcollid',
# u'flags',
# u'assetName'

    