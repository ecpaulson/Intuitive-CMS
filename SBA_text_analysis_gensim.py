__author__ = 'elisabethpaulson'

########## THIS FILE PERFORMS TEXT ANALYSIS ON THE FEMA CONTENT AND CREATES A CORPUS AND DICTIONARY FROM THE CONTENT

from standardize_web_content import *
from nltk.corpus import stopwords
from collections import defaultdict
from gensim import corpora, models, similarities
from pprint import pprint
import nltk

texts=[nltk.word_tokenize(text) for text in standard_text]
texts=[[word for word in sentences if word.lower() not in stopwords.words("english")] for sentences in texts]

chunktexts=[nltk.pos_tag(sentences) for sentences in texts]
patterns="""
            VP:{<V.*><DT>?<JJ>?<CD>?<NN.*>}
            VP2:{<VBZ>*<RB>+}
            NP:{<CD>?<DT>?<JJ>*<NN.*>}
            V: {<VBP>*}
            N:{<NN.*>}
            CD: {<CD>}
"""
NPchunker=nltk.RegexpParser(patterns)

from nltk.stem.snowball import SnowballStemmer
st=SnowballStemmer('english')

chunkedtext=[]
for text in chunktexts:
    temp=[]
    result=NPchunker.parse(text)
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

# # KEEP ONLY NOUNS
# texts=[nltk.pos_tag(sentences) for sentences in texts]
# texts=[[word for word in sentences if word[1]=='NNP']for sentences in texts]
# texts=[[word[0] for word in sentences] for sentences in texts]

# # REDUCE NOUNS TO STEMS
# from nltk.stem.snowball import SnowballStemmer
# st=SnowballStemmer('english')
# texts=[[st.stem(word) for word in sentences] for sentences in texts]

# SAVE DICTIONARY
dictionary=corpora.Dictionary(texts)
dictionary.save("SBA.dict")
#print(dictionary)

# SAVE CORPUS OF DESCRIPTIONS
SBAcorpus=[dictionary.doc2bow(text) for text in texts]
#print FEMAcorpus[:5]

corpora.MmCorpus.serialize('SBA.mm',SBAcorpus)
SBAcorpus=corpora.MmCorpus("SBA.mm")

# TF-IDF
SBAtfidf=models.TfidfModel(SBAcorpus)
SBAcorpus_tfidf=SBAtfidf[SBAcorpus]
#print FEMAcorpus_tfidf
#
# # LSI Model
# FEMAlsi=models.LsiModel(FEMAcorpus_tfidf,id2word=dictionary,num_topics=100)
# FEMAcorpus_lsi=FEMAlsi[FEMAcorpus_tfidf]
# #pprint(FEMAcorpus_lsi)
# #pprint(FEMAlsi.print_topics(5))
#
# LDA Model
SBAlda=models.LdaModel(SBAcorpus,id2word=dictionary,num_topics=50)
SBAcorpus_lda=SBAlda[SBAcorpus]
#pprint(SBAlda.print_topics(5,5))

# # HDP Model
# FEMAhdp=models.HdpModel(FEMAcorpus_tfidf,id2word=dictionary)
# FEMAcorpus_hdp=FEMAhdp[FEMAcorpus_tfidf]
# #pprint(hdp.print_topics(10,topn=5))


#for doc in corpus_lsi:
#    doc=sorted(doc,key=lambda  item: -item[1])
#    print(doc)



##### # FIND WHAT TOPIC BEST MATCHES GIVEN TERM
# doc="loan application" #Make up query term
# vec_bow=dictionary.doc2bow(doc.lower().split())
# print vec_bow
# vec_lda=SBAlda[vec_bow]
# print(vec_lda) # print vector that scores each document according to how well it matches query
#
# # WHICH WHICH DOCUMENT BEST MATCHES TERM
# index=similarities.MatrixSimilarity(SBAlda[SBAcorpus])
# print index
# index.save('SBA.index')
# #index=similarities.MatrixSimilarity.load('FEMA.index')
#
# # PRINT TOP 5 FEMA DOCUMENTS THAT BEST MATCH QUERY TERM
# sims=index[vec_lda]
# sims=sorted(enumerate(sims),key=lambda  item: -item[1])
# print sims[:10]
# for i in sims[:10]:
#    print(standard_descriptions[i[0]])
#    print(standard_links[i[0]])




