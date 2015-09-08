__author__ = 'elisabethpaulson'
from twitter import *
import re
from collections import defaultdict
from nltk.corpus import stopwords
from gensim import corpora, models, similarities
from pprint import pprint
from elasticsearch import Elasticsearch
es=Elasticsearch()
import nltk
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.text import TokenSearcher


# MUST HAVE RUN GatherTweets.py BEFORE THIS TO CREATE THE ELASTICSEARCH DATABASE

tweets=[]
for m in range(1000):
    res = es.get(index="sentiment", doc_type='hurricanetweets',id=m)
    tweets.append(res['_source']['message'])
# for m in range(1000):
#     res = es.get(index="sentiment", doc_type='FEMAtweets',id=m)
#     tweets.append(res['_source']['message'])
# for m in range(1000):
#    res = es.get(index="sentiment", doc_type='floodtweets',id=m)
#    tweets.append(res['_source']['message'])
# for m in range(1000):
#    res = es.get(index="sentiment", doc_type='emergencytweets',id=m)
#    tweets.append(res['_source']['message'])

std_FEMAtweets=[]
for x in tweets:
    y=x.upper()
    y=re.sub(r'[^A-Z#]',' ',y)
    y=re.sub(r'[\w]*RT[\w]*',r' ',y)
    y=re.sub(r'[\w]*FEMA[\w]*',r' ',y)
    y=re.sub(r'# ',r' ',y)
    y=re.sub(r'@[\w]*','',y)
    y=re.sub(r' [A-Z] ','',y)
    y.replace('HTTP','')
    y=re.sub(r'HTTP',r' ',y)
    y.replace('  ',' ')
    if y!='':
        std_FEMAtweets.append(y)


texts=[nltk.word_tokenize(tweet) for tweet in std_FEMAtweets]
texts=[[word for word in sentences if word.lower() not in stopwords.words("english")] for sentences in texts]

# KEEP ONLY NOUNS
texts=[nltk.pos_tag(sentences) for sentences in texts]
texts=[[word for word in sentences if word[1]=='NNP']for sentences in texts]
texts=[[word[0] for word in sentences] for sentences in texts]

texts=[[word for word in sentences if len(word)>2] for sentences in texts]

print(texts[:5])

words=[]
for text in texts:
    words+=text

freq=FreqDist(words)
print freq.most_common(50)

katrinatweets=[text for text in texts if 'KATRINA' in text]
print katrinatweets
words=[]
for text in katrinatweets:
    words+=text
freq=FreqDist(words)
print freq.most_common(50)