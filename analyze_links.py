__author__ = 'elisabethpaulson'

from bs4 import BeautifulSoup
import urllib
from elasticsearch import Elasticsearch
import datetime

es=Elasticsearch()
td=datetime.timedelta(hours=1)


results = es.search(index="stream",
                    doc_type="SBA",
                    body={"query":
                            {'bool':
                                 {'must':[
                                     {"term":{"flag": "yes"}},
                                     {'range':{'date':
                                             {'from':datetime.datetime.now()-td,
                                            'to': datetime.datetime.now()}}}]}
                            }
                          },
                    size=20)
print results['hits']['total']
for x in results['hits']['hits']:
    article_text=x['_source']['article_text']
    article_title=x['_source']['article_title']
    matches=es.search(index='web_content',
              doc_type='SBA',
              size=5,
              body={'query':
                        {'more_like_this':{
                            'fields':['text','description^2'],
                            'like_text':article_text+article_title,
                            'min_term_freq':1,
                            'max_query_terms':20
                        }}})
    print matches['hits']['total']
    print matches['hits']['max_score']
    print matches
    # es.delete_by_query(index='article_topics',
    #              doc_type='SBAcontent',
    #              body={'query':{'match_all':{}}})
    texts=[]
    titles=[]
    links=[]
    scores=[]
    for match in matches['hits']['hits']:
        texts.append(match['_source']['text'])
        titles.append(match['_source']['description'])
        links.append(match['_source']['link'])
        scores.append(match['_score'])
    article_link=x['_source']['link']
    es.index(index='article_topics',
             doc_type='SBAcontent',
             body={'article_title':article_title,
                    'article_text':article_text,
                   'article_link':article_link,
                   'content_titles':titles,
                   'content_texts':texts,
                   'content_links':links,
                   'content_scores':scores})

