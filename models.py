import arrow
import datetime
import peewee

db = peewee.SqliteDatabase('wxnews.db', threadlocals=True)

class BaseModel(peewee.Model):
    class Meta:
        database = db

class NewsItem(BaseModel):

    url_hash = peewee.CharField(unique=True)
    title = peewee.CharField()
    summary = peewee.TextField()
    title = peewee.CharField()
    link = peewee.CharField()
    source = peewee.CharField()
    published_date = peewee.CharField()
    published_ts = peewee.IntegerField()
    inserted_ts = peewee.IntegerField()

    @property
    def published_datetime_eastern(self):
        dt = arrow.get(self.published_ts).to('US/Eastern')
        return '%s %s' % (dt.format('MM/DD/YYYY h:mm a'), dt.datetime.strftime('%Z'))

    # @property
    # def published_date_eastern(self):
    #     dt = arrow.get(self.published_ts).to('US/Eastern').floor('day')
    #     return dt.format('MM/DD/YYYY')

    def __repr__(self):
        return self.title

if __name__ == "__main__":
    db.connect()
    db.create_table(NewsItem)
