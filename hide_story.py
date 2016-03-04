import peewee
import sys

from models import NewsItem

if len(sys.argv) < 2:
    sys.exit('Usage: $ python hide_story.py <story id>')
else:
    id = sys.argv[1]
    
try:
    id = int(id)
except ValueError:
    sys.exit("Invalid Story ID")

# Try to fetch the item
try:
    item = NewsItem.get(NewsItem.id==id)
except peewee.DoesNotExist:
    sys.exit("Error! News Item with ID %d not found" % id)

print 'You are attempting to hide story id %d' % id
print 'Headline: %s' % item.title

confirm = raw_input("Are you sure? Y/n: ")
if confirm == 'Y':
    item.hidden = True
    item.save()
