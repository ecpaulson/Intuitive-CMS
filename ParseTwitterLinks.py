from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup as bsoup
import requests

from readability.readability import Document
import urllib

es = Elasticsearch()

results = es.search(index="stream",
                    doc_type="SBA",
                    body={"query":
                          {"filtered":
                           {"filter":
                            {"term":
                             {"link_processed": "no"}
                             }
                            }
                           }
                          },
                    _source="link",
                    sort={"created_on": "asc"},
                    size=100)

for item in results['hits']['hits']:
    try:
        r = requests.get(item["_source"]['link'][0])
        readable_article = Document(r.text).summary()
        soup = bsoup(readable_article, 'lxml')
        article_text = soup.get_text(" ").encode('utf-8')
        article_url = r.url
        article_title = Document(r.text).short_title().encode('utf-8')

        doc ={"doc": {"article_title": article_title,
               "article_url": article_url,
               "article_text": article_text,
               "link_processed": "yes"
               }}

        es.update(index=item["_index"],
                      doc_type=item["_type"],
                      id=item["_id"],
                      body=doc)
        print "Success!"
    except: pass