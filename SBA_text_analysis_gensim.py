__author__ = 'elisabethpaulson'

########## THIS FILE PERFORMS TEXT ANALYSIS ON THE SBA CONTENT AND CREATES A CORPUS AND DICTIONARY FROM THE CONTENT

from standardize_web_content import *
from nltk.corpus import stopwords
from collections import defaultdict
from gensim import corpora, models, similarities
from pprint import pprint
import nltk
from nltk.stem.snowball import SnowballStemmer
st=SnowballStemmer('english')

texts=[nltk.word_tokenize(text) for text in standard_text]
texts=[[word for word in sentences if word.lower() not in stopwords.words("english")] for sentences in texts]

###### USING POS TAGGING #########
# chunktexts=[nltk.pos_tag(sentences) for sentences in texts]
# print chunktexts[87]
# patterns="""
#                 VP:{<V.*><DT>?<JJ.*>?<NN.*>}
#                 NP:{<DT>?<JJ>*<NN.*>}
#                 N:{<NN.*>}
#     """
# NPchunker=nltk.RegexpParser(patterns)
# print "Starting chunking"
# chunkedtext=[]
# for text in chunktexts:
#     temp=[]
#     result=NPchunker.parse(text)
#     #print result
#     for phrase in result:
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
# print "Done Chunking!"
# print chunkedtext[87]

##### USING BIGRAM CHUNKING ##################
bigrams=[]
for sentence in texts:
    temp=[]
    for i in range(len(sentence)-1):
        temp.append(st.stem(sentence[i])+' '+st.stem(sentence[i+1]))
    bigrams.append(temp)

### USES BOTH 1-GRAMS and BIGRAMS
# onegrams=[[st.stem(word) for word in sentences] for sentences in texts]
# bigrams=[bigram+onegram for bigram in bigrams for onegram in onegrams]

## SAVE DICTIONARY
# dictionary=corpora.Dictionary(chunkedtext)
dictionary=corpora.Dictionary(bigrams)
dictionary.save("SBA.dict")
print("Made Dictionary!")
#
# # SAVE CORPUS OF DESCRIPTIONS
# SBAcorpus=[dictionary.doc2bow(text) for text in chunkedtext]
SBAcorpus=[dictionary.doc2bow(text) for text in bigrams]
corpora.MmCorpus.serialize('SBA.mm',SBAcorpus)
SBAcorpus=corpora.MmCorpus("SBA.mm")
#
# # TF-IDF
# SBAtfidf=models.TfidfModel(SBAcorpus)
# SBAcorpus_tfidf=SBAtfidf[SBAcorpus]
SBAtfidf=models.TfidfModel(SBAcorpus)
SBAcorpus_tfidf=SBAtfidf[SBAcorpus]
# #print FEMAcorpus_tfidf
# #
# LDA Model
SBAlda=models.LdaModel(SBAcorpus,id2word=dictionary,num_topics=50)
SBAcorpus_lda=SBAlda[SBAcorpus]
print "Finished LDA modeling!"
#pprint(SBAlda.print_topics(5,5))

###### FIND WHAT TOPIC BEST MATCHES GIVEN TERM
doc="disaster loan" #Make up query term
doc=doc.lower().split()
doc_bigram=[]
for i in range(len(doc)-1):
    doc_bigram.append(st.stem(doc[i])+' '+st.stem(doc[i+1]))
# doc_bigram=doc_bigram+doc
print doc_bigram
vec_bow=dictionary.doc2bow(doc_bigram)

#### FOR POS TAGGING #####
# doc=doc.lower().split()
# print doc
# doc=nltk.pos_tag(doc)
# print doc
# doc=NPchunker.parse(doc)
# print doc
# for phrase in doc:
#     try:
#         phrase.label()
#         print 'A'
#         string=''
#         m=0
#         for word in phrase:
#             print 'word',word
#             if m==0:
#                 print 'B',word[0]
#                 string+=st.stem(word[0])
#                 print string
#                 m+=1
#             else:
#                 print 'C',word[0]
#                 string+=' '+st.stem(word[0])
#                 print string
#         temp.append(string)
#     except:
#         pass
# chunk=temp
# print chunk
# vec_bow=dictionary.doc2bow(chunk)
print vec_bow
vec_lda=SBAlda[vec_bow]
print(vec_lda) # print vector that scores each document according to how well it matches query

# WHICH WHICH DOCUMENT BEST MATCHES TERM
index=similarities.MatrixSimilarity(SBAlda[SBAcorpus])
index.save('SBA.index')
#index=similarities.MatrixSimilarity.load('FEMA.index')

# PRINT TOP 5 FEMA DOCUMENTS THAT BEST MATCH QUERY TERM
sims=index[vec_lda]
sims=sorted(enumerate(sims),key=lambda  item: -item[1])
print sims[:10]
for i in sims[:10]:
   print(standard_descriptions[i[0]])
   print(standard_links[i[0]])




