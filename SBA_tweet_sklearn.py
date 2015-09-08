__author__ = 'elisabethpaulson'

from elasticsearch import Elasticsearch
es=Elasticsearch()
from sklearn.datasets import fetch_20newsgroups
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics
from sklearn.decomposition import NMF
import re
import json
import pandas as pd
from pprint import pprint

from sklearn.cluster import KMeans, MiniBatchKMeans

############## FIRST PERFORM ANALYSIS ON FEMA WEB CONTENT #################
file="SBA-web-content.json"
myfile=open(file,'r').read()
results=json.loads(myfile)
data=pd.DataFrame.from_dict(results,orient='columns')
text=[]
for item in data.text:
    temp=''
    for x in item:
        if 'redirected' not in x:
            temp+=x
    text.append(temp)

descriptions=data.description
descriptions=map(str,descriptions)
#text=data.text
#text=map(str,text)
links=data.link
links=map(str,links)

standard_descriptions=[]
standard_links=[]
standard_text=[]

# STANDARDIZE LINKS AND DESCRIPTIONS
m=0
for x in text:
    y = x.replace('/',' ').replace('-',' ').replace('&','').replace('.\'',' ').replace(',','').replace('\[0-9]','').replace('.',' ').upper()  #split / and - into separated words
    y=''.join([i for i in y if not i.isdigit()])
    y=y.replace('[','').replace(']','').replace('U\'','').replace('\'',' ')
    y=re.sub(r'[\w]*[\\\.\-\&\/\(\)\"\:]+[\w]*', r'', y)
    if y!='':
        standard_text.append(y)
        standard_descriptions.append(descriptions[m])
        standard_links.append(links[m])
    m=m+1

vectorizer = TfidfVectorizer(max_df=0.5,min_df=2, stop_words='english')

vectorizer2 = TfidfVectorizer(min_df=10, stop_words='english',max_features=20)

# ANALYSIS ON EACH PAGE SEPARATELY
V = vectorizer.fit_transform(standard_text)

# ANALYSIS ON ALL FEMA CONTENT TOGETHER
words=[doc.split() for doc in standard_text]
words=''
for doc in standard_text:
    words+=doc
words=words.split()

W = vectorizer2.fit_transform(words)
terms = vectorizer2.get_feature_names()

print W

print terms

# ##### NOW ANALYZE TWITTER DATA ######
# tweets=[]
# for m in range(1000):
#     res = es.get(index="sentiment", doc_type='FEMAtweets',id=m)
#     tweets.append(res['_source']['message'])
#
# std_FEMAtweets=[]
# for x in tweets:
#     y=x.upper()
#     y=re.sub(r'[^A-Z#]',' ',y)
#     y=re.sub(r'[\w]*RT[\w]*',r'',y)
#     y=re.sub(r'[\w]*FEMA[\w]*',r'',y)
#     y=re.sub(r'# ',r'',y)
#     y=re.sub(r'@[\w]*','',y)
#     y=re.sub(r' [A-Z] ','',y)
#     y=re.sub(r'HTTP','',y)
#     y=re.sub(r'HTTPS','',y)
#     if y!='':
#         std_FEMAtweets.append(y)
#
# #print std_FEMAtweets
#
# X = vectorizer.fit_transform(std_FEMAtweets)
# #print X
#
# # svd=TruncatedSVD(5)
# # lsa=make_pipeline(svd,Normalizer(copy=False))
# # X=lsa.fit_transform(X)
# # explained_variance = svd.explained_variance_ratio_.sum()
# # print explained_variance
#
# km=MiniBatchKMeans(n_clusters=10)
# #km=KMeans()
#
# km.fit(X)
#
# print("Top terms per cluster:")
# order_centroids = km.cluster_centers_.argsort()[:, ::-1]
# terms = vectorizer.get_feature_names()
# for i in range(10):
#     print("Cluster %d:" % i)
#     print(" ".join([terms[ind] for ind in order_centroids[i, :10]]))
#
# nmf=NMF(n_components=10,random_state=1).fit(X)
#
# for topic_idx, topic in enumerate(nmf.components_):
#     print("Topic #%d:" % topic_idx)
#     print(" ".join([terms[i]
#                     for i in topic.argsort()[:-10 - 1:-1]]))
