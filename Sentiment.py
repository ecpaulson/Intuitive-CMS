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
#es = Elasticsearch('http://127.0.0.1:9200')
# es = Elasticsearch(
#     ['localhost', 'otherhost'],
#     http_auth=('user', 'secret'),
#     port=443,
#     use_ssl=True,
#     verify_certs=True,
#     ca_certs=certifi.where(),
# )

class TweetStreamListener(StreamListener):

    # on success
    def on_data(self, data):
        # decode json
        dict_data = json.loads(data)
        text=dict_data["text"]
        print text
        text=text.upper()
        text=re.sub(r'RT','',text)
        text=re.sub(r'HTTP.*','',text)
        text=re.sub(r'[^A-Z ]','',text)
        text=nltk.word_tokenize(text)
        text=[word for word in text if word.lower() not in stopwords.words("english")]
        text=[st.stem(word) for word in text]
        text=' '.join(text)
        print text
        # pass tweet into TextBlob
        tweet = TextBlob(dict_data["text"])

        # output sentiment polarity
        print tweet.sentiment.polarity

        # determine if sentiment is positive, negative, or neutral
        if tweet.sentiment.polarity < 0:
            sentiment = "negative"
        elif tweet.sentiment.polarity == 0:
            sentiment = "neutral"
        else:
            sentiment = "positive"

        # output sentiment
        print sentiment

        # medias = dict_data['entities']['urls']
        # print medias[0]['expanded_url']
        # add text and sentiment info to elasticsearch
        print datetime.datetime.now()
        es.index(index="streaming3",
                 doc_type="GL",
                 body={"user": dict_data["user"]["screen_name"],
                       'date': datetime.datetime.now(),
                       "message": text,
                       # "url": dict_data["urls"]["expanded_url"],
                       "polarity": tweet.sentiment.polarity,
                       "subjectivity": tweet.sentiment.subjectivity,
                       "sentiment": sentiment})

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
    stream.filter(track=['loan','loans','grant','grants'])