import arrow
import codecs
import jinja2
import os
import sys

CUR_DIR = os.path.dirname(os.path.realpath(__file__))

from models import NewsItem

# Set up the template engine to look in the current directory
template_loader = jinja2.FileSystemLoader('templates')
template_env = jinja2.Environment(loader=template_loader)

# Load the template file
template_file = "report.tpl.txt"
template = template_env.get_template(template_file)

# Load all the news items from the past week
seven_days_ago_ts = arrow.utcnow().ceil('hour').replace(days=-2).timestamp
news_items = NewsItem.select().where(NewsItem.published_ts>seven_days_ago_ts)

# Create a dictionary with all the stories grouped by source
sources = {}
for news_item in news_items:

    if not sources.has_key(news_item.source):
        sources[news_item.source] = {
            'items': [],
            'name': news_item.source,
        }
        
    # Add the news item
    sources[news_item.source]['items'].append(news_item)

# Sort the news items for each key
for key in sources.keys():
    sources[key]['items'].sort(key=lambda o:o.published_ts)

# Render the template
context = { 'sources': sources }
output = template.render(context)

# Save the output
filepath = os.path.join(CUR_DIR, 'output/report.txt')
with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(output)
