import pymongo;
import json;
import csv;
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from stop_words import get_stop_words
import re, collections
from preprocess import *

cachedStopWords = stopwords.words("english")
from pymongo import MongoClient;
client = MongoClient('localhost',27017);
db = client['yideas'];
collection = db.review;


index=0;
p_stemmer = PorterStemmer()
db.cleanedReview.remove();
for post in collection.find():
    reviewText = post["text"];
    current_line = removePunctuation(reviewText.lower()).split(' ')
    current_line = [stem(word) for word in current_line if word not in cachedStopWords]
    current_line = " ".join(current_line)
    post["text"] = ''.join([i for i in current_line if (i.isalpha() or i==' ')])
    db.cleanedReview.insert_one(post);

