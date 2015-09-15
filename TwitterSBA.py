__author__ = 'elisabethpaulson'


# TOPIC ANALYSIS ON TWITTER DATA

from gensim import corpora, models, similarities
from pprint import pprint
from elasticsearch import Elasticsearch
es=Elasticsearch()
import nltk
import datetime
import pandas as pd
import funcy as fp
import csv

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

### THIS SECTION PERFORMS TOPIC CLUSTERING USING GENSIM. CAN BE IGNORED IF USING SKLEARN INSTEAD #####
# texts=[nltk.word_tokenize(tweet) for tweet in tweets]
#
# texts=[[word for word in text if len(word)>2] for text in texts]
#
# # PULL OUT NOUN AND VERB PHRASES
#
# chunktexts=[nltk.pos_tag(sentences) for sentences in texts]
# patterns="""
#             VP:{<V.*><DT>?<JJ.*>?<NN.*>}
#             NP:{<DT>?<JJ>*<NN.*>}
#             N:{<NN.*>}
# """
# #VP2:{<VBZ>+<RB>+}
# #            V: {<VBP>*}
#
# NPchunker=nltk.RegexpParser(patterns)
#
# from nltk.stem.snowball import SnowballStemmer
# st=SnowballStemmer('english')
#
# chunkedtext=[]
# for text in chunktexts:
#     #print text
#     temp=[]
#     result=NPchunker.parse(text)
#     print result
#     for phrase in result:
#         #print phrase
#         #if 'small/JJ' not in phrase:
#         try:
#             phrase.label()
#             string=''
#             m=0
#             for word in phrase:
#                 if m==0:
#                     string+=st.stem(word[0])
#                     m+=1
#                 else: string+=' '+st.stem(word[0])
#             temp.append(string)
#         except: pass
#     chunkedtext.append(temp)
#
# chunkedtext=[[phrase for phrase in text if 'small' not in phrase]for text in chunkedtext]
#
# # SAVE DICTIONARY
# # dictionary1=corpora.Dictionary(texts) # This one is without POS tagging
# # dictionary1.save("GLtweets.dict")
# dictionary2=corpora.Dictionary(chunkedtext) # This one is for POS analysis
# dictionary2.save("GLtweetschunked.dict")
# #
# #SAVE TWEETS AS CORPUS
# # corpus1=[dictionary1.doc2bow(text) for text in texts]
# # corpora.MmCorpus.serialize('GLtweets.mm',corpus1)
# # corpus1=corpora.MmCorpus("GLtweets.mm")
# corpus2=[dictionary2.doc2bow(text) for text in chunkedtext]
# corpora.MmCorpus.serialize('GLtweetschunked.mm',corpus2)
# corpus2=corpora.MmCorpus("GLtweetschunked.mm")
#
# # TF-IDF
# # tfidf1=models.TfidfModel(corpus1)
# # corpus_tfidf1=tfidf1[corpus1]
# tfidf2=models.TfidfModel(corpus2)
# corpus_tfidf2=tfidf2[corpus2]
#
# # LSI model
# lsi=models.LsiModel(corpus_tfidf2,id2word=dictionary2,num_topics=5)
# pprint(lsi.print_topics(5,8))
#
# # LDA model for tweets related to SBA
# # lda1=models.LdaModel(corpus_tfidf1,id2word=dictionary1,num_topics=5)
# # pprint(lda1.print_topics(5,8)) #print first 10 topics
# lda2=models.LdaModel(corpus_tfidf2,id2word=dictionary2,num_topics=5)
# pprint(lda2.print_topics(5,8)) #print first 10 topics
# corpus_lda=lda2[corpus_tfidf2]
# #for doc in corpus_lda:
# #    print(doc)
# #

#### CODE FROM pyLDAvis ########

# def _normalize(array):
#    return pd.DataFrame(array).\
#       apply(lambda row: row / row.sum(), axis=1).values
#
# def _extract_data(topic_model, corpus, dictionary):
#    doc_lengths = [sum([t[1] for t in doc]) for doc in corpus]
#
#    term_freqs_dict = fp.merge_with(sum, *corpus)
#
#    vocab = dictionary.token2id.keys()
#    print len(vocab)
#
#    beta = 0.01
#    term_freqs = [term_freqs_dict.get(tid, beta) for tid in dictionary.token2id.values()]
#
#    gamma, _ = topic_model.inference(corpus)
#    doc_topic_dists = _normalize(gamma)
#
#    topics = topic_model.show_topics(formatted=False, num_words=len(vocab), num_topics=topic_model.num_topics)
#    print topics
#    topics_df = pd.DataFrame([dict((y,x) for x, y in tuples) for tuples in topics])[vocab]
#    print topics_df
#
#    #for i in range(len(vocab)):
#
#    topics_df.to_csv('topicdata.csv')
#    topic_term_dists = topics_df.values
#
#    return {'topic_term_dists': topic_term_dists, 'doc_topic_dists': doc_topic_dists,
#            'doc_lengths': doc_lengths, 'vocab': vocab, 'term_frequency': term_freqs}
#
# def prepare(topic_model, corpus, dictionary):
#     opts = fp.merge(_extract_data(topic_model, corpus, dictionary))
#     return opts
#
# opts=prepare(lda2,corpus2,dictionary2)
