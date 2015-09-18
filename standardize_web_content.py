__author__ = 'elisabethpaulson'
import json
import pandas as pd
from nltk.corpus import stopwords
from nltk.cluster import GAAClusterer
import re
from collections import defaultdict
from gensim import corpora, models, similarities
from pprint import pprint
import nltk
from nltk.stem.snowball import SnowballStemmer
st=SnowballStemmer('english')
from elasticsearch import Elasticsearch
es=Elasticsearch()
import csv

# MUST RUN SCRAPY SPIDER FIRST TO GENERATE JSON FILE
file="SBA-web-content.json"
myfile=open(file,'r').read()
results=json.loads(myfile)
data=pd.DataFrame.from_dict(results,orient='columns')
text=[]
for item in data.text:
    temp=''
    for x in item:
        if 'redirected' not in x:
            temp+=x+' '
    text.append(temp)
descriptions=[]
for item in data.description:
    temp=''
    for x in item:
        temp+=x+' '
    descriptions.append(temp)
#text=data.text
#text=map(str,text)
links=data.link
links=map(str,links)

es.delete_by_query(index='web_content',
                 doc_type='SBA',
                 body={'query':{'match_all':{}}})

standard_descriptions=[]
standard_links=[]
standard_text=[]

# STANDARDIZE LINKS AND DESCRIPTIONS
m=0
for m in range(len(text)):
    y = text[m].replace('/',' ').replace('-',' ').replace('&','').replace('.','').replace(',','').replace('(','').replace(')','').lower()  #split / and - into separated words
    y=re.sub(r':',' ',y)
    y=re.sub(r'businesses|business|small|sba','',y)
    z = descriptions[m].replace('/',' ').replace('-',' ').replace('&','').replace('.','').replace(',','').replace('(','').replace(')','').lower()  #split / and - into separated words
    z=z.replace('|','').replace('the us small business administration','').replace('sbagov','')
    z=re.sub(r':',' ',z)
    z=re.sub(r'businesses|business|small|sba','',z)
    #z=str.replace(' | the us small busi administr | sbagov','',z)
    if y!='':
        standard_text.append(y)
        standard_descriptions.append(z)
        standard_links.append(links[m])
    y=y.split()
    stemmed_text=[st.stem(word) for word in y]
    stemmed_text=' '.join(stemmed_text)
    z=z.split()
    stemmed_descr=[st.stem(word) for word in z]
    stemmed_descr=' '.join(stemmed_descr)
    result=es.search_exists(index='web_content',
         doc_type='SBA',
         body={"query":
                    {"match":{"description":{"query": descriptions[m],'operator':'and'}}}})
    if result==False:
        print stemmed_descr
        es.index(index='web_content',
             doc_type='SBA',
             body={'link':links[m],
                 'text': text[m],
                  'description':descriptions[m],
                  'stemmed text':stemmed_text,
                   'stemmed descr':stemmed_descr
                  })
