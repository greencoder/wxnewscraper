import arrow
import codecs
import jinja2
import os

CUR_DIR = os.path.dirname(os.path.realpath(__file__))

from models import NewsItem

def reformat_date(datestring):
    return arrow.get(datestring).format('dddd, MMMM D, YYYY')

# Set up the template engine to look in the current directory
template_loader = jinja2.FileSystemLoader('templates')
template_env = jinja2.Environment(loader=template_loader)

# Adding filters to enviroment to make them visible in the template
template_env.filters['format_date'] = reformat_date

# Load the template file
template_file = "index.tpl.html"
template = template_env.get_template(template_file)

# Load all the news items
three_days_ago = arrow.utcnow().to('US/Eastern').replace(hours=-72).format('YYYY-MM-DD')
news_items = NewsItem.select().where(NewsItem.published_date > three_days_ago)
news_items.order_by(NewsItem.published_ts)

# Render the template
context = {'news_items': news_items, 'updated_eastern': arrow.utcnow().to('US/Eastern') }
output = template.render(context)

# Save the output
filepath = os.path.join(CUR_DIR, 'output/sources.html')
with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(output)
