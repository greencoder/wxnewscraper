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

    published_date = arrow.get(date).to('US/Eastern').date().strftime('%Y-%m-%d')
    published_ts = arrow.get(date).to('UTC').timestamp

    skippable_headline_prefixes = (
        'D.C. area forecast',
        'PM Update',
    )

    # Skip the story if it starts with "D.C. area forecast"
    prefix_match = False
    for prefix in skippable_headline_prefixes:
        if entry.title.startswith(prefix):
            prefix_match = True
    
    if prefix_match:
        print 'Skipping story'
        continue
    
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
    item.published_date = published_date
    item.published_ts = published_ts
    item.inserted_ts = arrow.utcnow().timestamp

    item.save()
