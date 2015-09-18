from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup as bsoup
import requests
import datetime
import urllib

from readability.readability import Document
#import urllib
td=datetime.timedelta(hours=1)

es = Elasticsearch()

results = es.search(index="stream",
                    doc_type="SBA",
                    body={"query":
                          {"filtered":
                           {"filter":
                                {'bool':
                                     {'must':[
                                         {"term":{"link_processed": "no"}},
                                         {'range':{'date':
                                                 {'from':datetime.datetime.now()-td,
                                                'to': datetime.datetime.now()}}}]}
                                }
                            }
                           }
                          },
                    _source="link",
                    sort={"date": "des"},
                    size=50)

for item in results['hits']['hits']:
    print item
    try:
        r = requests.get(item["_source"]['link'][0])
        res=urllib.urlopen(r.url)
        http_message=res.info()
        main=http_message.maintype
        print main
        if main=='text':
            print "Made it in"
            readable_article = Document(r.text).summary()
            #print readable_article
            soup = bsoup(readable_article, 'lxml')
            article_text = soup.get_text(" ").encode('utf-8')
            article_url = r.url
            article_title = Document(r.text).short_title().encode('utf-8')

            print "Success!"
            print article_title
            ## SEE IF MLT QUERY RESULTS IN MORE THAN 10 OF THE SAME ARTICLES WITHIN X HOURS
            matches = es.search(index="stream",
                            doc_type="SBA",
                            body={"query":
                                    {'bool':{
                                         'must':[
                                             {"match":{"article_title":{"query": article_title,'operator':'and'}}},
                                             {'range':{'date':
                                                     {'from':datetime.datetime.now()-td,
                                                    'to': datetime.datetime.now()}}}],
                                        'must_not':[
                                         {"match":{"article_title":{"query": 'Twitter','operator':'and'}}},
                                        {"match":{"article_title":{"query": 'Forbidden','operator':'and'}}}]}
                                    }
                                  },
                            size=5)
            print matches['hits']['total']
            if matches['hits']['total']>5:
                print "flag change"
                tag= es.search_exists(index="stream",
                    doc_type="SBA",
                    body={"query":
                                {'bool':
                                     {'must':[
                                        {"match":{"article_title": article_title}},
                                         {"match":{"flag": 'yes'}}]
                          }}})
                print tag
                if tag==False:
                    flag='yes'
                    print flag
                else:
                    flag='no'
                    print flag
            else:flag='no'
            doc ={"doc":{"article_title": article_title,
                   "article_url": article_url,
                   "article_text": article_text,
                   "link_processed": "yes",
                         'flag':flag
                   }}
        else:
            doc ={"doc":{"article_title": '',
                   "article_url": '',
                   "article_text": '',
                   "link_processed": "yes",
                         'flag':'yes'
                   }}

        es.update(index=item["_index"],
                      doc_type=item["_type"],
                      id=item["_id"],
                      body=doc)
    except:
        doc ={"doc":{"link_processed": "yes",
                     'flag':'no'
               }}
        es.update(index=item["_index"],
                      doc_type=item["_type"],
                      id=item["_id"],
                      body=doc)
        pass