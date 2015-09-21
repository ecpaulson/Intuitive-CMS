__author__ = 'elisabethpaulson'


# TOPIC ANALYSIS ON TWITTER DATA

from elasticsearch import Elasticsearch
es=Elasticsearch()
import datetime


# MUST HAVE RUN GatherTweets.py BEFORE THIS TO CREATE THE ELASTICSEARCH DATABASE

td=datetime.timedelta(hours=1)

result=es.search(
    index='stream',
    doc_type='SBA',
    size=5000,
    body={
        'query':{
            'filtered':{
                'filter':{
                    'range':{
                        'date':{
                            'from':datetime.datetime.now()-td,
                            'to': datetime.datetime.now()
                            }
                        }
                    }
                }
            }
    }
    )

print result['hits']['total']

tweets=[]
full_tweets=[]
for tweet in result['hits']['hits']:
    tweets.append(tweet['_source']['message'])
    full_tweets.append(tweet['_source']['full message'])

