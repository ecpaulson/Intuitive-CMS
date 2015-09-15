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

descriptions=data.description
descriptions=map(str,descriptions)
#text=data.text
#text=map(str,text)
links=data.link
links=map(str,links)

standard_descriptions=[]
standard_links=[]
standard_text=[]

# STANDARDIZE LINKS AND DESCRIPTIONS
m=0
for x in text:
    y = x.replace('/',' ').replace('-',' ').replace('&','').replace('.','').replace(',','').replace('(','').replace(')','').lower()  #split / and - into separated words
    y=re.sub(r':',' ',y)
    y=re.sub(r'businesses|business|small|sba','',y)
    if y!='':
        standard_text.append(y)
        standard_descriptions.append(descriptions[m])
        standard_links.append(links[m])
    m=m+1