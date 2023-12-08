import numpy as np
import os
import requests
import syllables
from bs4 import BeautifulSoup as bs
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
import re

pos=np.loadtxt("positive-words.txt",dtype="str")
neg=np.loadtxt("negative-words.txt",dtype="str")

path="C:\\Users\\omkar\\Documents\\scraping\\StopWords\\"
stopwords=np.array([],dtype="str")

for i in os.listdir(path):
    temp=np.loadtxt(path+i,dtype="str",usecols=0,delimiter="|")
    stopwords=np.concatenate((stopwords,temp),axis=0)
stopdict=set(stopwords)

df=pd.read_excel("Output.xlsx",header=0)

pattern= re.compile(r'\b(I|you|he|she|it|we|you|they|me|you|him|her|it|(?-i:us)|you|them|mine|yours|his|hers|its|ours|yours|theirs)\b',re.I)

for idx,urlid,url,*temp in df.itertuples():
    page=requests.get(url)
    soup=bs(page.content,"html.parser")
    try:
        text="".join([i.text for i in soup.find("div",class_="td-post-content tagdiv-type").find_all("p")])
        cleantext=[i for i in text.split() if i not in stopdict]
        words=len(text.split())
        letters=len(text)
        avglpw=letters/words
        sentences=np.char.count(text,".")
        avgwps=words/sentences
        avglps=letters/sentences
        pscore=sum(1 for i in text.split() if i in pos)
        nscore=sum(1 for i in text.split() if i in neg)
        polarity=(pscore-nscore)/((pscore+nscore)+0.000001)
        subjectivity=(pscore+nscore)/(words+0.000001)
        pronouns=len(pattern.findall(text))
        sylarr=np.array([syllables.estimate(i) for i in text.split()])
        avgspw=sylarr.sum()/words
        complex=len(sylarr[np.where(sylarr>2)])
        complexper=complex/words*100
        fogindex=0.4*(avgwps+complex)
        newrow=[urlid,url,pscore,nscore,polarity,subjectivity,avglps,complexper,fogindex,avgwps,complex,words,avgspw,pronouns,avglpw]
        # sia = SentimentIntensityAnalyzer()
        # poldict=sia.polarity_scores(text)
        # print(poldict)
        # print(*newrow, sep=" - ")
        print(idx)
        df.loc[idx]=newrow
    except:
        print(idx,"fail")
        pass
print(df.head())
df.to_excel("Output.xlsx")


