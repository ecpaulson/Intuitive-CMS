__author__ = 'elisabethpaulson'

####### THIS FILE CLUSTERS TWEETS USING KMEANS FROM THE SKLEARN MODULE #############
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, MiniBatchKMeans
#from TwitterSBA import *
#from ParseTwitterLinks import *
from nltk.corpus import stopwords
import nltk
from nltk.stem.snowball import SnowballStemmer
import datetime

st=SnowballStemmer('english')
es=Elasticsearch()

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

def pos_tokenizer(s): #define a tokenizer that uses POS tagging
    texts=nltk.word_tokenize(s)

    texts=[word for word in texts if len(word)>2]

    # PULL OUT NOUN AND VERB PHRASES
    chunktext=nltk.pos_tag(texts)
    patterns="""
                VP:{<V.*><DT>?<JJ.*>?<NN.*>}
                NP:{<DT>?<JJ>*<NN.*>}
                N:{<NN.*>}
    """
    NPchunker=nltk.RegexpParser(patterns)

    from nltk.stem.snowball import SnowballStemmer
    st=SnowballStemmer('english')

    #print text
    temp=[]
    result=NPchunker.parse(chunktext)
    #print result
    for phrase in result:
        try:
            phrase.label()
            string=''
            m=0
            for word in phrase:
                if m==0:
                    string+=st.stem(word[0])
                    m+=1
                else: string+=' '+st.stem(word[0])
            temp.append(string)
        except: pass
    return temp

def bigram_tokenizer(s):
    texts=nltk.word_tokenize(s)
    texts=[word for word in texts if word.lower() not in stopwords.words("english")]
    doc_bigram=[]
    for i in range(len(texts)-1):
        # CAN CHOOSE TO STEM OR NOT STEM
        #doc_bigram.append(texts[i]+' '+texts[i+1])
        doc_bigram.append(st.stem(texts[i])+' '+st.stem(texts[i+1]))
    return doc_bigram


# DEFINE VECTORIZER
vectorizer = TfidfVectorizer(max_df=0.5,min_df=2, stop_words='english',tokenizer=bigram_tokenizer)#,ngram_range=(1,2))

# FIT AND TRANSFORM ALL TWEETS
X = vectorizer.fit_transform(tweets)
#print X

# svd=TruncatedSVD(5)
# lsa=make_pipeline(svd,Normalizer(copy=False))
# X=lsa.fit_transform(X)
# explained_variance = svd.explained_variance_ratio_.sum()
# print explained_variance

n_clusters=10 #specify number of clusters
#km=MiniBatchKMeans(n_clusters=n_clusters) #could try MiniBatchKMeans instead of KMeans
km=KMeans(n_clusters=n_clusters)

km.fit(X)

# PRINT TOP TERMS PER CLUSTER
topic_phrases=[]
print("Top terms per cluster:")
order_centroids = km.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names()
for i in range(n_clusters):
    print("Cluster %d:" % i)
    topic_phrases.append(", ".join([terms[ind] for ind in order_centroids[i, :n_clusters]]))
    print(", ".join([terms[ind] for ind in order_centroids[i, :n_clusters]]))

# PREDICT WHICH TOPIC EACH TWEET BELONGS TO
vec=km.predict(X)

# PUT TOPIC INFO INTO NEW ES INDEX
for i in range(len(vec)):
    k= str(vec[i])
    result = es.search(index="stream",
                        doc_type="SBA",
                        size=100,
                        body={"query":
                              {"match":{"full message":{"query": full_tweets[i],"operator":'and'}}}
                              }
                                )
    for item in result['hits']['hits']:
        doc ={"doc": {"topic": k,
               "#tweets_in_topic": len([x for x in vec if x==vec[i]]),
               "phrases": topic_phrases[vec[i]]
               }}

        es.update(index=item["_index"],
                      doc_type=item["_type"],
                      id=item["_id"],
                      body=doc)

# PRINT ALL TWEETS FOR EACH TOPIC
for i in range(n_clusters):
    print 'TOPIC',i
    for j in range(len(tweets)):
        if vec[j]==i:
            print full_tweets[j]

####### VISUALIZE 2-D REPRESENTATION #########################################

reduced_data=PCA(n_components=2).fit_transform(X.toarray())
kmeans=KMeans(n_clusters=n_clusters)
kmeans.fit(reduced_data)
h=.02
x_min, x_max = reduced_data[:, 0].min(), reduced_data[:, 0].max()
y_min, y_max = reduced_data[:, 1].min(), reduced_data[:, 1].max()
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

# Obtain labels for each point in mesh. Use last trained model.
Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])


# Put the result into a color plot
Z = Z.reshape(xx.shape)
plt.figure(1)
plt.clf()
plt.imshow(Z, interpolation='nearest',
           extent=(xx.min(), xx.max(), yy.min(), yy.max()),
           cmap=plt.cm.Paired,
           aspect='auto', origin='lower')

plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
# Plot the centroids as a white X
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1],
            marker='x', s=169, linewidths=3,
            color='w', zorder=10)
plt.title('K-means clustering on the digits dataset (PCA-reduced data)\n'
          'Centroids are marked with white cross')
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.xticks(())
plt.yticks(())
#plt.show()


####### MeanShift algorithm ############################
# X=X.toarray()
#
# bandwith=estimate_bandwidth(X,quantile=.035)
# print bandwith
# ms=MeanShift(bandwidth=bandwith,bin_seeding=True)
#
# ms.fit(X)
#
# labels = ms.labels_
# print labels.shape
# cluster_centers = ms.cluster_centers_
#
# labels_unique = np.unique(labels)
# print labels_unique
# n_clusters_ = len(labels_unique)
#
# print("number of estimated clusters : %d" % n_clusters_)
#
# print("Top terms per cluster:")
# order_centroids = ms.cluster_centers_.argsort()[:, ::-1]
# terms = vectorizer.get_feature_names()
# for i in range(n_clusters_):
#     print("Cluster %d:" % i)
#     print(" ".join([terms[ind] for ind in order_centroids[i, :n_clusters]]))
#
# vec=ms.predict(X)
#
# for i in range(n_clusters_):
#     print 'TOPIC',i
#     for j in range(len(tweets)):
#         if vec[j]==i:
#             print full_tweets[j]
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
# nmf=NMF(n_components=10,random_state=1).fit(X)
#
# for topic_idx, topic in enumerate(nmf.components_):
#     print("Topic #%d:" % topic_idx)
#     print(" ".join([terms[i]
#                     for i in topic.argsort()[:-10 - 1:-1]]))
