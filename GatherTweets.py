__author__ = 'elisabethpaulson'
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
from elasticsearch import Elasticsearch
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
st=SnowballStemmer('english')
import datetime

# import twitter keys and tokens
from config import *

# create instance of elasticsearch
es=Elasticsearch()

class TweetStreamListener(StreamListener):

    # on success
    def on_data(self, data):
        # decode json
        dict_data = json.loads(data)
        text=dict_data["text"]
        print text
        link=re.findall(r'http[^ ]*',text)
        print link
        text=text.lower()

        es.index(index='temp',
                 doc_type='temp',
                 id=1,
                 refresh=True,
                 body={
                     "message": text
                 })
        result=es.search_exists(
            index='temp',
            doc_type='temp',
            body={
                'query':{'bool':{'should':[{'terms':{
                    'message':['loans','grant','grants','loan','pay','budget','debt','money', 'save','spend','invest','tax','taxes','dollar','apply','application','paid','credit','interest','bank','debtor','repay','borrow','lend','lender','federal']}
                    }],'minimum_should_match':1}}
                })

        if result==True: #If the incoming tweet matches the query
            print "MATCH!"
            text=re.sub(r'rt |RT ','',text)
            text=re.sub(r'&amp','',text)
            text=re.sub(r'http.*','',text)
            text=re.sub(r'@[a-zA-Z0-9]*','',text)
            text=re.sub(r'\'','',text)
            text=re.sub(r'[^a-zA-Z ]',' ',text)
            #text=nltk.word_tokenize(text)
            #text=[word for word in text if word.lower() not in stopwords.words("english")]
            #text=[st.stem(word) for word in text]
            #text=' '.join(text)
            tweet = TextBlob(dict_data["text"])

            # determine if sentiment is positive, negative, or neutral
            if tweet.sentiment.polarity < 0:
                sentiment = "negative"
            elif tweet.sentiment.polarity == 0:
                sentiment = "neutral"
            else:
                sentiment = "positive"
            print datetime.datetime.now()
            if 'http' in dict_data["text"]: #if the tweet contains a link
                print 'contains link'
                es.index(index="stream",
                     doc_type="SBA",
                     body={"user": dict_data["user"]["screen_name"],
                           'date': datetime.datetime.now(),
                           "message": text,
                           "full message": dict_data["text"],
                           # "url": dict_data["urls"]["expanded_url"],
                           "polarity": tweet.sentiment.polarity,
                           "subjectivity": tweet.sentiment.subjectivity,
                           "sentiment": sentiment,
                           "link": link,
                           "link_processed":'no'
                            })
            else:
                es.index(index="stream",
                     doc_type="SBA",
                     body={"user": dict_data["user"]["screen_name"],
                           'date': datetime.datetime.now(),
                           "message": text,
                           "full message": dict_data["text"],
                           # "url": dict_data["urls"]["expanded_url"],
                           "polarity": tweet.sentiment.polarity,
                           "subjectivity": tweet.sentiment.subjectivity,
                           "sentiment": sentiment,
                           "link": "no link",
                           "link_processed":'yes'
                            })


        return True

    # on failure
    def on_error(self, status):
        print status

if __name__ == '__main__':

    # create instance of the tweepy tweet stream listener
    listener = TweetStreamListener()

    # set twitter keys/tokens
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # create instance of the tweepy stream
    stream = Stream(auth, listener)

    # search twitter for "congress" keyword
    stream.filter(track=['small business','small businesses','SBA','SBAgov','smallbiz'])