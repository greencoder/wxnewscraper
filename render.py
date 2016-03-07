import arrow
import codecs
import jinja2
import os

CUR_DIR = os.path.dirname(os.path.realpath(__file__))

from models import NewsItem

def reformat_date(datestring):
    return arrow.get(datestring).format('dddd, MMM. D, YYYY')

def get_source_url(source):
    """ Returns the URL that can be used for a source hyperlink """
    if source == 'Accuweather':
        return 'http://www.accuweather.com/en/weather-news'
    elif source == 'Capital WX Gang':
        return 'https://twitter.com/capitalweather'
    elif source == 'Weather Underground':
        return 'http://www.wunderground.com/news/'
    elif source == 'Weather Channel':
        return 'https://weather.com/news'
    elif source == 'NY Post':
        return 'http://nypost.com/tag/weather/'
    elif source == 'Star Tribune':
        return 'http://www.startribune.com/weather/'
    elif source == 'WeatherBug':
        return 'http://weather.weatherbug.com/news/'
    elif source == 'The Weather Network':
        return 'http://www.theweathernetwork.com/news/category/latest/'
    elif source == 'NY Times':
        return 'http://topics.nytimes.com/top/reference/timestopics/subjects/w/weather/index.html'
    elif source == 'Seattle Times':
        return 'http://blogs.seattletimes.com/today/category/weather-beat/'
    elif source == 'Science Daily':
        return 'http://feeds.sciencedaily.com/sciencedaily/earth_climate/weather'
    elif source == 'Weather 5280':
        return 'http://www.weather5280.com'
    else:
        return '#'

# Set up the template engine to look in the current directory
template_loader = jinja2.FileSystemLoader('templates')
template_env = jinja2.Environment(loader=template_loader)

# Adding filters to enviroment to make them visible in the template
template_env.filters['format_date'] = reformat_date
template_env.filters['get_source_url'] = get_source_url

# Load the template file
template_file = "index.tpl.html"
template = template_env.get_template(template_file)

# Load all the news items
three_days_ago = arrow.utcnow().to('US/Eastern').replace(hours=-72).format('YYYY-MM-DD')
news_items = NewsItem.select().where(
    NewsItem.published_date > three_days_ago,
    NewsItem.hidden == 0
)
news_items.order_by(NewsItem.published_ts)

# Render the template
context = {'news_items': news_items, 'updated_eastern': arrow.utcnow().to('US/Eastern') }
output = template.render(context)

# Save the output
filepath = os.path.join(CUR_DIR, 'output/sources.html')
with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(output)
