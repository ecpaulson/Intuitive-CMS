__author__ = 'elisabethpaulson'

from SBA_tweet_sklearn import *
from SBA_text_analysis_gensim import *
from ParseTwitterLinks import *

####### RELATE TWITTER DATA TO SBA WEB CONTENT #################

# IMPORT CORPUS FROM SBA WEBSITE
corpus=corpora.MmCorpus("SBA.mm")

# LOAD DICTIONARY
dictionary=corpora.Dictionary.load("SBA.dict")

### FIND SBA CONTENT THAT MATCHES THE TWITTER TOPICS, OR POINT OUT WHERE SIMILAR CONTENT DOES NOT EXIST

for i in range(n_clusters):
    print '\n Topic', i,'relates to:', topic_phrases[i]
    # FIND WHAT TOPIC BEST MATCHES TERM
    doc=[] #this method keeps phrases together (using the POS tagging)
    for word in topic_phrases[i].split(', '):
        doc.append(word)

    # doc='' #this method separates topic into individual words. If this option is used, need to change options in SBA_text_analysis_gensim
    # for word in topic_phrases[i]:
    #     doc+=word

    vec_bow=dictionary.doc2bow(doc)
    #vec_bow=dictionary.doc2bow(doc.lower().split()) #use this when second option above is chosen
    percentage=len(vec_bow)/(len(doc)*1.0) #percentage of phrases in doc that are also found in the dictionary

    if percentage>.4: #we want at least X% of phrases in doc to actually appear in the dictionary. If not, we found a gap in content
        vec_lda=SBAlda[vec_bow] #transform bow into LDA space
        index=similarities.MatrixSimilarity.load('SBA.index')
        #index=similarities.MatrixSimilarity.load('SBA.index') #can use this instead if not 1st run

        # PRINT TOP 5 SBA DOCUMENTS THAT BEST MATCH QUERY TERM IF THEY EXIST
        sims=index[vec_lda]
        sims=sorted(enumerate(sims),key=lambda  item: -item[1])
        print sims[:5]
        if sims[0][1]>.8: #only want to consider content with similarity score >.8
            for i in sims[:5]:
               print(standard_descriptions[i[0]])
               print(standard_links[i[0]])
        else: #if no content is similar enough, show tweets relating to topic
            print "There is no SBA content that matches this topic very well. Here are some tweets relating to topic",i,":"
            m=0
            for j in range(len(tweets)):
                if vec[j]==i:
                    if m<3:
                        print full_tweets[j]
                        m+=1
                    results = es.search(index="stream",
                        doc_type="SBA",
                        size=1,
                        body={"query":
                              {"match":{"full message":{"query": full_tweets[j],"operator":'and'}}}
                              }#,
                              # {'query':{'filtered':{'filter':{'range':{'date':{'from':datetime.datetime.now()-td,
                              #   'to': datetime.datetime.now()}}}}}
                              #   }
                                )
            for item in results['hits']['hits']:
                if item['_source']['link']!='no link':
                    #print item
                    try:
                        article_text=article_text+item['_source']['article_text']+item['_source']['article_title']
                        #print article
                    except:
                        pass
            print "There have been",len([x for x in vec if x==vec[i]]),'tweets like these in the last 5 hours!'
            article_text=article_text.lower().split()
            article_bigram=[]
            for k in range(len(article_text)-1):
                article_bigram.append(st.stem(article_text[k])+' '+st.stem(article_text[k+1]))
            vec_bow=dictionary.doc2bow(article_bigram)
            print "We tried to find SBA content that relates to the tweeted link, and found",100*len(vec_bow)/(1.0*len(article_bigram)),'percent matching of bigrams.'
            if len(vec_bow)/(1.0*len(article_bigram))>0:
                index=similarities.MatrixSimilarity.load('SBA.index')
                sims=index[SBAlda[vec_bow]]
                sims=sorted(enumerate(sims),key=lambda item: -item[1])
                #print SBAlda[vec_bow]
                print sims[:3]
                score=sims[0][1]
                print score
                m=0
                while sims[m][1]==score:
                    print(standard_descriptions[sims[m][0]])
                    print(standard_links[sims[m][0]])
                    m+=1
                print "There have been",len([x for x in vec if x==vec[i]]),'tweets like these in the last 5 hours!'
    else: #if no content is similar enough, show tweets relating to topic
        print "Not enough words in this topic relate to SBA content. Here's what people are talking about:"
        m=0
        article_text=''
        for j in range(len(tweets)):
            if vec[j]==i:
                if m<3:
                    print full_tweets[j]
                    m=m+1
                results = es.search(index="stream",
                        doc_type="SBA",
                        size=1,
                        body={"query":
                              {"match":{"full message":{"query": full_tweets[j],"operator":'and'}}}
                              }#,
                              # {'query':{'filtered':{'filter':{'range':{'date':{'from':datetime.datetime.now()-td,
                              #   'to': datetime.datetime.now()}}}}}
                              #   }
                                )
                for item in results['hits']['hits']:
                    if item['_source']['link']!='no link':
                        #print item
                        try:
                            article_text=article_text+item['_source']['article_text']+item['_source']['article_title']
                            #print article
                        except:
                            pass
        print "There have been",len([x for x in vec if x==vec[i]]),'tweets like these in the last 5 hours!'
        article_text=article_text.lower().split()
        article_bigram=[]
        for k in range(len(article_text)-1):
            article_bigram.append(st.stem(article_text[k])+' '+st.stem(article_text[k+1]))
        vec_bow=dictionary.doc2bow(article_bigram)
        print "We tried to find SBA content that relates to the tweeted link, and found",100*len(vec_bow)/(1.0*len(article_bigram)),'percent matching of bigrams.'
        if len(vec_bow)/(1.0*len(article_bigram))>0:
            index=similarities.MatrixSimilarity.load('SBA.index')
            sims=index[SBAlda[vec_bow]]
            sims=sorted(enumerate(sims),key=lambda item: -item[1])
            #print SBAlda[vec_bow]
            print sims[:3]
            score=sims[0][1]
            print score
            m=0
            while sims[m][1]==score:
                print(standard_descriptions[sims[m][0]])
                print(standard_links[sims[m][0]])
                m+=1
            print "There have been",len([x for x in vec if x==vec[i]]),'tweets like these in the last 5 hours!'

