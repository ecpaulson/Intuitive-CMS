__author__ = 'elisabethpaulson'

from twitter import *
import re
from nltk import corpus
from pprint import pprint
from elasticsearch import Elasticsearch
es=Elasticsearch()
import nltk
import numpy as np
import pandas as pd
from scipy.sparse import lil_matrix
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import rescal
from scipy.sparse import lil_matrix
from rescal import als
import datetime

import optics

# MUST HAVE RUN GatherTweets.py BEFORE THIS TO CREATE THE ELASTICSEARCH DATABASE


td=datetime.timedelta(hours=6)

result=es.search(
    index='streaming4',
    doc_type='GL',
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
for tweet in result['hits']['hits']:
    tweets.append(tweet['_source']['message'])
# tweets=[]
# for m in range(200):
#     res = es.get(index="streaming4", doc_type='GL',id=m)
#     tweets.append(res['_source']['message'])

texts=[nltk.word_tokenize(tweet) for tweet in tweets]
texts=[[word for word in sentences if word.lower() not in nltk.corpus.stopwords.words("english")] for sentences in texts]

texts=[[word for word in sentences if len(word)>2] for sentences in texts]
print texts[:5]
words=[]
for text in texts:
    words+=text
print len(words)

fdist=nltk.probability.FreqDist(words)
words=sorted(list(set(words)))

texts=[[word for word in text if fdist[word]>40] for text in texts]
words=[word for word in words if fdist[word]>40]
print len(words)
print texts[:5]

print words[:5]

texts=[[words.index(word) for word in text] for text in texts]
print texts[:5]

T = np.zeros([len(words),len(words),2])

#relation 0 : word B 1 spot after word A
for row in texts:
    for n in range(len(row)-1):

        T[row[n],row[n+1],0] = 1

#relation 1: word B 1 or more spots after word A
for row in texts:
    for n in range(len(row)-1):
       for m in range(n+1,len(row)):
            T[row[n],row[m],1] = 1

X = [lil_matrix(T[:, :, k]) for k in range(2)]

#Decompose tensor using RESCAL-ALS
A, R, fit, itr, exectimes = als(X, 60, init='nvecs', lambda_A=10, lambda_R=10)


RD, CD, order = optics.optics(A, 2)
Aordered = A[order]
wordsordered = np.array([words[i] for i in order])
print wordsordered
RDordered = RD[order]
CDordered = CD[order]

plt.rcParams['figure.figsize'] = (15, 10)
fig, ax = plt.subplots()

index = range(len(words))[::-1]

x = range(len(index)) #just show 0 - end
y = CDordered[index]
labels = wordsordered[index]
print labels
plt.plot(x,y,'o-')

for i in x:
    print labels[i],y[i]
    ax.annotate('%s' % labels[i], fontsize=8, xy=(x[i],y[i]), xytext = (1, 8*len(labels[i])), textcoords = 'offset points', rotation = 'vertical')

plt.show()
plt.savefig('clusters_4_relations',dpi=150)