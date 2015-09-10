from bs4 import BeautifulSoup as soup
import feedparser
import requests
from readability.readability import Document
from elasticsearch import Elasticsearch

es = Elasticsearch()

# Select feed type:

# Google News RSS Feed
d = feedparser.parse('http://news.google.com/news?q=grants+loans+small+business&output=rss')

# Google Alert RSS Feed
# d = feedparser.parse('https://www.google.com/alerts/feeds/03803877705654670462/4544370163122525742')

# Iterate through current feed entries 
# NOTE: currently doesn't check for duplicates (i.e., may import same 
# entries as previously processed); for testing purposes only.
for entry in d.entries:
	# SELECT ONE (based on feed type):

	# Google News RSS Entry Link
    r = requests.get(entry.link)
    # Google Alert RSS Entry Link
    # r = requests.get(entry.links[0].href)

    # Extract article text, title, and url
    readable_article = Document(r.text).summary()
    article_html = soup(readable_article, 'lxml')
    article_text = article_html.get_text(" ").encode('utf-8')
    article_url = r.url
    article_title = Document(r.text).short_title().encode('utf-8')

    # Place relevant info into document for easy ES insertion.
	# NOTE: "published" field is not currently processed; date format 
	# differs between Google News and Alert feeds
    doc = {"doc": {"article_title": article_title,
                   "article_url": article_url,
                   "article_text": article_text,
                   "published": entry.published}}

    # Insert document into ES (change as necessary)
    es.index(index="news-test",
              doc_type="rss",
              body=doc)
