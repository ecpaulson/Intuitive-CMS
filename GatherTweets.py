__author__ = 'elisabethpaulson'

##### THIS FILE GATHERS TWEETS BASED ON KEYWORDS "FEMA" "HURRICANE" "FLOOD" AND "EMERGENCY" ##########

import tweepy
from textblob import TextBlob
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, streaming_bulk
from pprint import pprint

es=Elasticsearch()

auth = tweepy.OAuthHandler('lRBqclAO9jIuVn1i2GyamBDCI', 'V9CIUsTUU9OFrEM3DgEaKTZjfgrrnNfTG7zMWRrDjWT0Rrf9rt')
auth.set_access_token('341804649-NCg92iUdPM2XiEvzIOqW4YF89jkMxO8AtZRj0KWK', 'AnAQRpJRaXNZgefmN1xCvc6cLyjJaH0xH0qMsj8Qh4IHz')
api=tweepy.API(auth)
pprint(api.rate_limit_status())
public_tweets=[status for status in tweepy.Cursor(api.search, q='FEMA',lan='english').items(1000)]
m=0
for tweet in public_tweets:
    #print(tweet)
    datablob=TextBlob(tweet.text)
    #print datablob
    #print datablob.sentiment.polarity
    if datablob.sentiment.polarity < 0:
        sentiment = "negative"
    elif datablob.sentiment.polarity == 0:
        sentiment = "neutral"
    else:
        sentiment = "positive"
    # output sentiment
    doc={"date": tweet.created_at,
                   "message": tweet.text,
                   "polarity": datablob.sentiment.polarity,
                   "subjectivity": datablob.sentiment.subjectivity,
                   "sentiment": sentiment}
    es.index(index="sentiment",
             doc_type="FEMAtweets",
                 id=m,
             body=doc)
    m=m+1

public_tweets=[status for status in tweepy.Cursor(api.search, q='hurricane',lan='english').items(1000)]
n=0
for tweet in public_tweets:
    #print(tweet)
    datablob=TextBlob(tweet.text)
    #print datablob
    #print datablob.sentiment.polarity
    if datablob.sentiment.polarity < 0:
        sentiment = "negative"
    elif datablob.sentiment.polarity == 0:
        sentiment = "neutral"
    else:
        sentiment = "positive"
    # output sentiment
    doc={"date": tweet.created_at,
                   "message": tweet.text,
                   "polarity": datablob.sentiment.polarity,
                   "subjectivity": datablob.sentiment.subjectivity,
                   "sentiment": sentiment}
    es.index(index="sentiment",
             doc_type="hurricanetweets",
                 id=n,
             body=doc)
    n=n+1

public_tweets=[status for status in tweepy.Cursor(api.search, q='flood',lan='english').items(1000)]
q=0
for tweet in public_tweets:
    #print(tweet)
    datablob=TextBlob(tweet.text)
    #print datablob
    #print datablob.sentiment.polarity
    if datablob.sentiment.polarity < 0:
        sentiment = "negative"
    elif datablob.sentiment.polarity == 0:
        sentiment = "neutral"
    else:
        sentiment = "positive"
    # output sentiment
    doc={"date": tweet.created_at,
                   "message": tweet.text,
                   "polarity": datablob.sentiment.polarity,
                   "subjectivity": datablob.sentiment.subjectivity,
                   "sentiment": sentiment}
    es.index(index="sentiment",
             doc_type="floodtweets",
                 id=q,
             body=doc)
    q=q+1

public_tweets=[status for status in tweepy.Cursor(api.search, q='emergency',lan='english').items(1000)]
r=0
for tweet in public_tweets:
    #print(tweet)
    datablob=TextBlob(tweet.text)
    #print datablob
    #print datablob.sentiment.polarity
    if datablob.sentiment.polarity < 0:
        sentiment = "negative"
    elif datablob.sentiment.polarity == 0:
        sentiment = "neutral"
    else:
        sentiment = "positive"
    # output sentiment
    doc={"date": tweet.created_at,
                   "message": tweet.text,
                   "polarity": datablob.sentiment.polarity,
                   "subjectivity": datablob.sentiment.subjectivity,
                   "sentiment": sentiment}
    es.index(index="sentiment",
             doc_type="emergencytweets",
                 id=r,
             body=doc)
    r=r+1