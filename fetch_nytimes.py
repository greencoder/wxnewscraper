import arrow
import bs4
import feedparser
import hashlib
import peewee
import unidecode
import sys

from models import NewsItem

source_url = 'http://topics.nytimes.com/top/reference/timestopics/subjects/w/weather/index.html?rss=1'
feed = feedparser.parse(source_url)

for entry in feed.entries:
    
    link = entry.link
    url_hash = hashlib.md5(link).hexdigest()
    date = entry.published_parsed

    published_date = arrow.get(date).to('US/Eastern').date().strftime('%Y-%m-%d')
    published_ts = arrow.get(date).to('UTC').timestamp

    # Make sure the date isn't greater than today (it happens)
    if published_date > arrow.now().to('US/Eastern').floor('day').format('YYYY-MM-DD'):
        published_date = arrow.now().to('US/Eastern').floor('day').format('YYYY-MM-DD')
        published_ts = arrow.now().to('US/Eastern').floor('day').timestamp

    # See if we already have this story
    try:
        NewsItem.get(NewsItem.url_hash==url_hash)
        print 'Item exists. Skipping.'
        continue
    except peewee.DoesNotExist:
        print 'Creating item.'
        item = NewsItem()

    headline = entry.title
    summary = entry.summary

    item.url_hash = url_hash
    item.link = link
    item.source = 'NY Times'
    item.title = headline
    item.summary = summary
    item.published_date = published_date
    item.published_ts = published_ts
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()
