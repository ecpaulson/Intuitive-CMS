__author__ = 'elisabethpaulson'

import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.datasets.samples_generator import make_blobs
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse
import re
from elasticsearch import Elasticsearch
es=Elasticsearch()
from scipy.linalg import svd
import matplotlib.pyplot as plt
from nltk import cluster
from mpl_toolkits.mplot3d import Axes3D
import datetime

###############################################################################
# TWITTER DATA
# tweets=[]
# for m in range(100):
#     res = es.get(index="sentiment", doc_type='hurricanetweets',id=m)
#     tweets.append(res['_source']['message'])
# for m in range(100):
#     res = es.get(index="sentiment", doc_type='FEMAtweets',id=m)
#     tweets.append(res['_source']['message'])
# for m in range(100):
#    res = es.get(index="sentiment", doc_type='floodtweets',id=m)
#    tweets.append(res['_source']['message'])
# for m in range(100):
#    res = es.get(index="sentiment", doc_type='emergencytweets',id=m)
#    tweets.append(res['_source']['message'])
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

#print std_FEMAtweets
vectorizer = TfidfVectorizer(max_df=0.5,min_df=2, stop_words='english')

W = vectorizer.fit_transform(tweets)
print vectorizer.get_feature_names()
WW=W.toarray()
WW=WW.transpose()
#WW=sparse.csc_matrix.toarray(W)
print WW.shape
# WWones=np.zeros([WW.shape[0],WW.shape[1]])
# for i in range(WW.shape[0]):
#     for j in range(WW.shape[1]):
#         if WW[i][j]>0: WWones[i][j]=1
U,S,Vt=svd(WW)

ratio=[S[i]/sum(S) for i in range(len(S))]
#plt.bar(np.arange(50),ratio[:50])
#plt.show()

# ONLY KEEP FIRST 20 DIMENSIONS
U=U[:,:20]
S=S[:20]
Vt=Vt[:20,:]

newVt=np.zeros([20,WW.shape[1]])
k=0
tweet_order=[0]
notused=[i for i in range(WW.shape[1])]
notused.remove(0)
newVt[:,0]=Vt[:,0]
for j in range(WW.shape[1]-1):
    sim=np.zeros(len(notused))
    for i in range(len(notused)):
        sim[i]=cluster.cosine_distance(Vt[:,k],Vt[:,notused[i]])
    ind=np.argsort(sim)
    newVt[:,j+1]=Vt[:,notused[ind[0]]]
    k=notused[ind[0]]
    tweet_order.append(k)
    notused.remove(notused[ind[0]])


print Vt
print newVt
fig, ax = plt.subplots(figsize=(30,8))
image=newVt
ax.imshow(image,interpolation='nearest',aspect='auto')
ax.set_title('sorted tweets')
plt.savefig('sortedtweets.png')
plt.show()

fig, ax = plt.subplots(figsize=(30,8))
image=Vt
ax.imshow(image,interpolation='nearest',aspect='auto')
ax.set_title('tweets')
plt.savefig('tweets.png')
plt.show()


# appended1=np.concatenate((Vt[0,:],U[:,0]))
# appended2=np.concatenate((Vt[1,:],U[:,1]))
# appended3=np.concatenate((Vt[2,:],U[:,2]))
# fig=plt.figure()
# ax=fig.add_subplot(111,projection='3d')
# ax.scatter(Vt[0,:],Vt[1,:],Vt[2,:],c='b')
# ax.scatter(U[:,0],U[:,1],U[:,2],c='r')
# plt.show()
###############################################################################

# # Compute clustering with MeanShift
#
# # The following bandwidth can be automatically detected using
# bandwidth = estimate_bandwidth(WW, quantile=0.05, n_samples=500)
# print bandwidth
# ms = MeanShift(bandwidth=bandwidth, bin_seeding=True,cluster_all=False)
# ms.fit(WW)
# labels = ms.labels_
# print labels.shape
# cluster_centers = ms.cluster_centers_
#
# labels_unique = np.unique(labels)
# n_clusters_ = len(labels_unique)
#
# print("number of estimated clusters : %d" % n_clusters_)
#
# ###############################################################################
# # Plot result
# import matplotlib.pyplot as plt
# from itertools import cycle
#
# plt.figure(1)
# plt.clf()
#
# colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
# for k, col in zip(range(n_clusters_), colors):
#     my_members = labels == k
#     cluster_center = cluster_centers[k]
#     plt.plot(WW[my_members, 0], WW[my_members, 1], col + '.')
#     plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
#              markeredgecolor='k', markersize=14)
# plt.title('Estimated number of clusters: %d' % n_clusters_)
# plt.show()
