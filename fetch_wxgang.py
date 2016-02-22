import arrow
import bs4
import feedparser
import hashlib
import peewee
import unidecode
import sys

from models import NewsItem

source_url = 'http://feeds.washingtonpost.com/rss/rss_capital-weather-gang'
feed = feedparser.parse(source_url)

for entry in feed.entries:
    
    link = entry.link
    url_hash = hashlib.md5(link).hexdigest()
    date = entry.published_parsed
    
    # See if we already have this story
    try:
        NewsItem.get(NewsItem.url_hash==url_hash)
        print 'Item exists. Skipping.'
        continue
    except peewee.DoesNotExist:
        print 'Creating item.'
        item = NewsItem()

    soup = bs4.BeautifulSoup(entry.description, 'html.parser')
    item.summary = unidecode.unidecode(soup.text.strip())
    item.title = unidecode.unidecode(entry.title)

    item.url_hash = url_hash
    item.link = link
    item.authors = ''
    item.source = 'Capital WX Gang'
    item.published_ts = arrow.get(date).to('UTC').timestamp
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()