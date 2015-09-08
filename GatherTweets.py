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
#from TwitterFEMA import *

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
        text=text.lower()
        text=re.sub(r'rt ','',text)
        text=re.sub(r'http.*','',text)
        text=re.sub(r'[^a-z ]','',text)
        #text=re.sub(r'appli[a-z]*',r'apply',text)
        text=nltk.word_tokenize(text)
        text=[word for word in text if word.lower() not in stopwords.words("english")]
        #text=[st.stem(word) for word in text]
        text=' '.join(text)
        # pass tweet into TextBlob
        tweet = TextBlob(dict_data["text"])
        print text
        # output sentiment polarity

        # determine if sentiment is positive, negative, or neutral
        if tweet.sentiment.polarity < 0:
            sentiment = "negative"
        elif tweet.sentiment.polarity == 0:
            sentiment = "neutral"
        else:
            sentiment = "positive"

        # output sentiment

        # medias = dict_data['entities']['urls']
        # print medias[0]['expanded_url']
        # add text and sentiment info to elasticsearch
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
                'query':{
                    #'query_string':{
                    #    'default_field':'message',
                    #    'query':'small business', 'loan',' pay budget debt money save spend invest tax dollar apply application paid credit interest bank debtor repay borrow lend lender federal job'
                    #},
                    'bool':{
                        'must_not':[
                            {
                            'term':{'message':'student'}
                            }
                        ],
                        'should':[
                            {
                            'terms':{
                                'message':['small business','small businesses','pay','budget','debt','money', 'save','spend','invest','tax','dollar','apply','application','paid','credit','interest','bank','debtor','repay','borrow','lend','lender','federal']}
                            }
                            ],
                        'minimum_should_match':1
                    }
                }
            }
        )



        if result==True:
            print "MATCH!"

            # # Now we have to chunk it and add it to the corpus, and label it according to a topic
            # chunk=nltk.word_tokenize(text)
            # chunk=[word for word in chunk if len(word)>2]
            # chunk=nltk.pos_tag(chunk)
            # chunkedtext=[]
            # result=NPchunker.parse(chunk)
            # #print result
            # for phrase in result:
            #     try:
            #         phrase.label()
            #         string=''
            #         m=0
            #         for word in phrase:
            #             if m==0:
            #                 string+=word[0]
            #                 m+=1
            #             else: string+=' '+word[0]
            #         chunkedtext.append(string)
            #     except: pass
            #
            # #dictionary2=corpora.Dictionary.add_documents(corpora.Dictionary(chunkedtext))
            # #dictionary2.save("GLtweetschunked.dict")
            # new_vec=dictionary2.doc2bow(chunkedtext)
            # print "1"
            # new_tfidf=tfidf2[new_vec]
            # print "2"
            # lda2.update(new_tfidf)
            # print "3"
            # print lda2[new_tfidf]
            # print '4'
            #
            # print lda2.get_document_topics(new_tfidf,minimum_probability=.7)

            es.index(index="stream",
                     doc_type="SBL",
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
    stream.filter(track=['small business','small businesses','SBA'])