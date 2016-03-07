import arrow
import bs4
import feedparser
import hashlib
import peewee
import unidecode
import sys

from models import NewsItem

source_url = 'http://www.weather5280.com/rss/'
feed = feedparser.parse(source_url)

for entry in feed.entries:
    
    link = entry.link
    url_hash = hashlib.md5(link).hexdigest()
    date = entry.published_parsed

    published_date = arrow.get(date).to('US/Eastern').date().strftime('%Y-%m-%d')
    published_ts = arrow.get(date).to('UTC').timestamp

    headline = entry.title
    summary = entry.summary

    if headline.startswith('The State of the Atmosphere'):
        headline = "(Denver) %s" % headline

    # See if we already have this story
    try:
        NewsItem.get(NewsItem.url_hash==url_hash)
        print 'Item exists. Skipping.'
        continue
    except peewee.DoesNotExist:
        print 'Creating item.'
        item = NewsItem()

    item.url_hash = url_hash
    item.link = link
    item.source = 'Weather 5280'
    item.title = headline
    item.summary = summary
    item.published_date = published_date
    item.published_ts = published_ts
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()
