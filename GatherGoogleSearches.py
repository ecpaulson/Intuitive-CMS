__author__ = 'elisabethpaulson'
import tweepy
from textblob import TextBlob
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, streaming_bulk
from pprint import pprint
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
st=SnowballStemmer('english')
import pandas as pd

es=Elasticsearch()

data=pd.read_csv('GSD.csv')

print data.dtypes
print data.Date[0]

print data[0]
m=0
for row in data:
    print row
    for rep in range(row.AvgDaily):
        text=row.Keyword
        text=re.sub(r'[^A-Z ]','',text)
        text=nltk.word_tokenize(text)
        text=[word for word in text if word.lower() not in stopwords.words("english")]
        text=[st.stem(word) for word in text]
        text=' '.join(text)
        doc={"date": row.Date,
                       "search": text}
        es.index(index="searchdata",
                 doc_type="GL",
                 id=m,
                 body=doc)
        m+=1