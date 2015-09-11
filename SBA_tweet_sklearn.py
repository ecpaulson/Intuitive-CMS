__author__ = 'elisabethpaulson'

from elasticsearch import Elasticsearch
es=Elasticsearch()
from sklearn.datasets import fetch_20newsgroups
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.decomposition import PCA
from sklearn.cluster import MeanShift, estimate_bandwidth
#from standardize_web_content import *
import numpy as np
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans, MiniBatchKMeans

############## FIRST PERFORM ANALYSIS ON FEMA WEB CONTENT #################

# vectorizer2 = TfidfVectorizer(min_df=5, stop_words='english',max_features=30,ngram_range=(1,3))
#
# # ANALYSIS ON EACH PAGE SEPARATELY
# V = vectorizer.fit_transform(standard_text)
#
# corpus=matutils.Sparse2Corpus(V,documents_columns=True)
#
# texts=[nltk.word_tokenize(text) for text in standard_text]
# texts=[[word for word in sentences if word.lower() not in stopwords.words("english")] for sentences in texts]
#
# print standard_text[:10]
# #print chunkedtext[:10]
#
# # ANALYSIS ON ALL FEMA CONTENT TOGETHER
# words=[doc.split() for doc in standard_text]
# words=''
# for doc in standard_text:
#     words+=doc
# words=words.split()
#
# W = vectorizer2.fit_transform(words)
# terms = vectorizer2.get_feature_names()


##### NOW ANALYZE TWITTER DATA ######

from TwitterSBA import *

def pos_tokenizer(s):
    import nltk

    texts=nltk.word_tokenize(s)

    texts=[word for word in texts if len(word)>2]

    # PULL OUT NOUN AND VERB PHRASES

    chunktext=nltk.pos_tag(texts)
    patterns="""
                VP:{<V.*><DT>?<JJ.*>?<NN.*>}
                NP:{<DT>?<JJ>*<NN.*>}
                N:{<NN.*>}
    """
    #VP2:{<VBZ>+<RB>+}
    #            V: {<VBP>*}

    NPchunker=nltk.RegexpParser(patterns)

    from nltk.stem.snowball import SnowballStemmer
    st=SnowballStemmer('english')

    #print text
    temp=[]
    result=NPchunker.parse(chunktext)
    #print result
    for phrase in result:
        #print phrase
        #if 'small/JJ' not in phrase:
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

vectorizer = TfidfVectorizer(max_df=0.5,min_df=2, stop_words='english',ngram_range=(1,3),tokenizer=pos_tokenizer)


X = vectorizer.fit_transform(tweets)
#print X

# svd=TruncatedSVD(5)
# lsa=make_pipeline(svd,Normalizer(copy=False))
# X=lsa.fit_transform(X)
# explained_variance = svd.explained_variance_ratio_.sum()
# print explained_variance

#km=MiniBatchKMeans(n_clusters=10)
n_clusters=10
km=KMeans(n_clusters=n_clusters)

km.fit(X)

topic_phrases=[]
print("Top terms per cluster:")
order_centroids = km.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names()
for i in range(n_clusters):
    print("Cluster %d:" % i)
    topic_phrases.append(", ".join([terms[ind] for ind in order_centroids[i, :n_clusters]]))
    print(", ".join([terms[ind] for ind in order_centroids[i, :n_clusters]]))

vec=km.predict(X)

for i in range(len(vec)):
    k= str(vec[i])
    es.index(index="topics",
                     doc_type="tweets",
                     id=i,
                     body={"topic_num": k,
                           "num_tweets": len([x for x in vec if x==vec[i]]),
                           "phrases": topic_phrases[vec[i]],
                           "full tweet":full_tweets[i],
                           "processed tweet": tweets[i]
                           })

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
plt.show()


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
