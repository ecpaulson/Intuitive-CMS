__author__ = 'elisabethpaulson'

from SBA_tweet_sklearn import *
#from SBA_text_analysis_gensim import *
#from ParseTwitterLinks import *
import re

####### RELATE TWITTER DATA TO SBA WEB CONTENT #################

### FIND SBA CONTENT THAT MATCHES THE TWITTER TOPICS, OR POINT OUT WHERE SIMILAR CONTENT DOES NOT EXIST
es.delete_by_query(index='topics',
                 doc_type='SBAcontent',
                 body={'query':{'match_all':{}}})
for i in range(n_clusters):
    print '\n Topic', i,'relates to:', topic_phrases[i]
    # FIND WHAT TOPIC BEST MATCHES TERM
    #doc=[] #this method keeps phrases together
    #for word in topic_phrases[i].split(', '):
    #     doc.append(word)

    temp='' #this method separates topic into individual words. If this option is used, need to change options in SBA_text_analysis_gensim
    for word in topic_phrases[i]:
        word=re.sub(r'\,','',word)
        temp+=word
    #vec_bow=dictionary.doc2bow(doc)
    doc=temp
    #doc=temp.lower().split()
    #doc=['apply','loan','disaster','apply disaster','disaster loan']
    print doc
    results = es.search(index="web_content",
        doc_type="SBA",
        body={"query" : {
                "bool":{
                    "should":[
                        {"match": {
                            "stemmed descr":{"query":doc}}}],
                    "minimum_should_match":2}}})
    #doc=' '.join(doc)
    #print doc
    # results=es.search(index='web_content',
    #           doc_type='SBA',
    #           size=5,
    #           body={'query':
    #                     {'more_like_this':{
    #                         'fields':['text','description^2'],
    #                         'like_text':doc,
    #                         'min_term_freq':1,
    #                         'max_query_terms':20
    #                     }}})
    # NEED A WAY TO CLEAR THE INDEX TOPICS EVERY RUN

    for item in results['hits']['hits']:
        print item['_source']['description']
        es.index(index='topics',
                 doc_type='SBAcontent',
                 body={'topics':i,
                     'score':item['_score'],
                       'text':item['_source']['text'],
                       'stemmed descr':item['_source']['stemmed descr'],
                       'link':item['_source']['link'],
                       'description':item['_source']['stemmed descr'],
                       'stemmed text':item['_source']['stemmed text']})


                #print "There have been",len([x for x in vec if x==vec[i]]),'tweets like these in the last 5 hours!'