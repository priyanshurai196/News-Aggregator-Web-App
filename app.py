# app.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import feedparser
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    link = db.Column(db.String(200))
    category = db.Column(db.String(50))
    pub_date = db.Column(db.DateTime)

@app.route('/')
def index():
    with app.app_context():
        articles = Article.query.all()
    return render_template('index.html', articles=articles)

def fetch_and_store_feed(url, category):
    with app.app_context():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            pub_date = entry.get('published_parsed')
            if pub_date:
                pub_date = datetime(*pub_date[:6], tzinfo=timezone.utc)
            else:
                pub_date = datetime.now(timezone.utc)

            # Determine the category based on article content or source feed
            title = entry.title.lower()
            content = entry.get('summary', '').lower()

            if any(keyword in title or keyword in content for keyword in ['terrorism', 'protest', 'political unrest', 'riot']):
                article_category = 'Terrorism/Protest/Political Unrest/Riot'
            elif any(keyword in title or keyword in content for keyword in ['positive', 'uplifting']):
                article_category = 'Positive/Uplifting'
            elif any(keyword in title or keyword in content for keyword in ['natural disaster']):
                article_category = 'Natural Disasters'
            else:
                article_category = 'Others'

            article = Article(
                title=entry.title,
                link=entry.link,
                category=article_category,
                pub_date=pub_date
            )
            db.session.add(article)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Example RSS feeds and categories
        feeds = {
            'CNN Top Stories': 'http://rss.cnn.com/rss/cnn_topstories.rss',
            'Quartz': 'http://qz.com/feed',
            'Fox News Politics': 'http://feeds.foxnews.com/foxnews/politics',
            'Reuters Business News': 'http://feeds.reuters.com/reuters/businessNews',
            'PBS NewsHour World': 'http://feeds.feedburner.com/NewshourWorld',
            'BBC News India': 'https://feeds.bbci.co.uk/news/world/asia/india/rss.xml'
            # Add more feeds and categories as needed
        }

        for category, feed_url in feeds.items():
            fetch_and_store_feed(feed_url, category)

    app.run(debug=True, port=5001)
