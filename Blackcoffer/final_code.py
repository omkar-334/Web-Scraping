import numpy as np
import os
import requests
import syllables
from bs4 import BeautifulSoup as bs
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
import re

# Loading Positive and Negative words from Master Dictionary
pos=np.loadtxt("MasterDictionary\\positive-words.txt",dtype="str")
neg=np.loadtxt("MasterDictionary\\negative-words.txt",dtype="str")

# Setting path and Initializing stopwords array
path="C:\\Users\\omkar\\Downloads\\Blackcoffer\\StopWords\\"
stopwords=np.array([],dtype="str")

# Loading stopwords from StopWords folder
for i in os.listdir(path):
    temp=np.loadtxt(path+i,dtype="str",usecols=0,delimiter="|")
    stopwords=np.concatenate((stopwords,temp),axis=0)
stopdict=set(stopwords)

# Reading the Output Data Structure
df=pd.read_excel("Output Data Structure.xlsx",header=0)

# Regex pattern for matching pronouns
pattern= re.compile(r'\b(I|you|he|she|it|we|you|they|me|you|him|her|it|(?-i:us)|you|them|mine|yours|his|hers|its|ours|yours|theirs)\b',re.I)
failcount=0

# Looping though the Output dataframe
for idx,urlid,url,*temp in df.itertuples():

    # Initializing BeautifulSoup object with the url
    page=requests.get(url)
    soup=bs(page.content,"html.parser")

    try:
        finder=soup.find("div",class_="td-post-content tagdiv-type")
        if finder is None:
            finder=soup.find_all("div",class_="tdb-block-inner td-fix-index")[14]

        text="".join([i.text for i in finder.find_all("p")])

        # Cleans the text based on the stopwords
        cleantext=[i for i in text.split() if i not in stopdict]
        words=len(text.split())
        letters=len(text)

        avglpw=letters/words # Average letters per word

        # Counts sentences based on '.' delimiter
        sentences=np.char.count(text,".")

        avgwps=words/sentences # Average words per sentence
        avglps=letters/sentences # Average letters per sentence

        # Calculating Positive score and Negative score
        pscore=sum(1 for i in text.split() if i in pos)
        nscore=sum(1 for i in text.split() if i in neg)

        # Calculating polarity and subjectivity based on given formulae
        polarity=(pscore-nscore)/((pscore+nscore)+0.000001)
        subjectivity=(pscore+nscore)/(words+0.000001)

        # Matching pronouns based on the regex pattern
        pronouns=len(pattern.findall(text))

        # Calulating number of syllables using the 'syllables' python library
        sylarr=np.array([syllables.estimate(i) for i in text.split()])
        avgspw=sylarr.sum()/words # Average syllables per word

        # Complex words - words with more than 2 syllables
        complex=len(sylarr[np.where(sylarr>2)])
        complexper=complex/words*100  # Percentage of complex words
        fogindex=0.4*(avgwps+complex)  # Fog Index

        # sia = SentimentIntensityAnalyzer()
        # poldict=sia.polarity_scores(text)
        # print(poldict)

        # Appending new row to the datafram
        newrow=[urlid,url,pscore,nscore,polarity,subjectivity,avglps,complexper,fogindex,avgwps,complex,words,avgspw,pronouns,avglpw]
        df.loc[idx]=newrow
        print(idx)
    except:
        print(idx,"fail")
        failcount+=1
        pass

print(f"Links failed - {failcount}")

# Writing the dataframe to output file
df.to_excel("Output.xlsx")
