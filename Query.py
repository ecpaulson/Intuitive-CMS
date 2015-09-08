__author__ = 'elisabethpaulson'

import tweepy
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import nltk
from nltk import corpus
import re

es=Elasticsearch()

# result=es.search(
#     index='streaming3',
#     doc_type='GL',
#     size=3000,
#     body={
#         'query':{
#             'match_all':{}
#         }
#     }
# )

result=es.search(
    index='streaming3',
    doc_type='GL',
    size=3000,
    body={
        'query':{
            'bool':{
                'should':[
                    {
                        "term":{'message': 'take out'}
                    },{
                        "term":{'message': 'pay'}
                    },{
                        "term":{'message': 'debt'}
                    },{
                        "term":{'message': 'money'}
                    },{
                        "term":{'message': 'save'}
                    },{
                        "term":{'message': 'spend'}
                    },{
                        "term":{'message': 'invest'}
                    },{
                        "term":{'message': 'tax'}
                    },{
                        "term":{'message': 'dollar'}
                    },{
                        "term":{'message': 'apply'}
                    },{
                        "term":{'message': 'applic'}
                    },{
                        "term":{'message': 'paid'}
                    }
                ]
                }
            }
        })
print result['hits']['total']

m=0
for hit in result['hits']['hits']:
    doc={"date": hit['_source']['date'],
               "user": hit['_source']['user'],
               "message": hit['_source']['message'],
               "polarity": hit['_source']['polarity'],
               "subjectivity": hit['_source']['subjectivity'],
               "sentiment": hit['_source']['sentiment']}
    es.index(index="filtered",
             doc_type="GL",
             id=m,
             body=doc)
    m=m+1


