__author__ = 'elisabethpaulson'


# TOPIC ANALYSIS ON TWITTER DATA

from gensim import corpora, models, similarities
from pprint import pprint
from elasticsearch import Elasticsearch
es=Elasticsearch()
import nltk
import datetime


# MUST HAVE RUN GatherTweets.py BEFORE THIS TO CREATE THE ELASTICSEARCH DATABASE

td=datetime.timedelta(hours=48)

result=es.search(
    index='stream',
    doc_type='SBL',
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

texts=[nltk.word_tokenize(tweet) for tweet in tweets]

texts=[[word for word in text if len(word)>2] for text in texts]

# PULL OUT NOUN AND VERB PHRASES

chunktexts=[nltk.pos_tag(sentences) for sentences in texts]
patterns="""
            VP:{<V.*><DT>?<JJ>?<NN|NNS><NN|NNS>?}
            VP2:{<VBZ>*<RB>+}
            NP:{<DT>?<JJ>*<NN|NNS><NN|NNS>?}
            V: {<VBP>*}
            N:{<NN|NNS><NN|NNS>?}
"""
NPchunker=nltk.RegexpParser(patterns)

from nltk.stem.snowball import SnowballStemmer
st=SnowballStemmer('english')

chunkedtext=[]
for text in chunktexts:
    temp=[]
    result=NPchunker.parse(text)
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
    chunkedtext.append(temp)

# REDUCE NOUNS TO STEMS
# from nltk.stem.snowball import SnowballStemmer
# st=SnowballStemmer('english')
print chunkedtext[:5]
# chunkedtext2=[]
# chu
# for sentence in chunkedtext[:2]:
#     for phrase in sentence:
#         temp=''
#         for word in phrase.split():
#             temp+=st.stem(word)+' '
#         chunkedtext2.append(temp)
# chunkedtext=[[[st.stem(word) for word in phrase.split()] for phrase in sentence] for sentence in chunkedtext]
# print chunkedtext[:5]


# SAVE DICTIONARY
# dictionary1=corpora.Dictionary(texts) # This one is without POS tagging
# dictionary1.save("GLtweets.dict")
dictionary2=corpora.Dictionary(chunkedtext) # This one is for POS analysis
dictionary2.save("GLtweetschunked.dict")
#
#SAVE TWEETS AS CORPUS
# corpus1=[dictionary1.doc2bow(text) for text in texts]
# corpora.MmCorpus.serialize('GLtweets.mm',corpus1)
# corpus1=corpora.MmCorpus("GLtweets.mm")
corpus2=[dictionary2.doc2bow(text) for text in chunkedtext]
corpora.MmCorpus.serialize('GLtweetschunked.mm',corpus2)
corpus2=corpora.MmCorpus("GLtweetschunked.mm")

# TF-IDF
# tfidf1=models.TfidfModel(corpus1)
# corpus_tfidf1=tfidf1[corpus1]
tfidf2=models.TfidfModel(corpus2)
corpus_tfidf2=tfidf2[corpus2]

# LDA model for tweets related to SBA
# lda1=models.LdaModel(corpus_tfidf1,id2word=dictionary1,num_topics=5)
# pprint(lda1.print_topics(5,8)) #print first 10 topics
lda2=models.LdaModel(corpus_tfidf2,id2word=dictionary2,num_topics=15)
pprint(lda2.print_topics(5,8)) #print first 10 topics
#corpus_lda=lda2[corpus_tfidf2]
#for doc in corpus_lda:
#    print(doc)
#
