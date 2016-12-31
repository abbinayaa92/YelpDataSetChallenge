import pandas as pd
import time
import redis
from flask import current_app
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from pymongo import MongoClient
import traceback


# def info(msg):
#     current_app.logger.info(msg)
reco = {}


def dumpRecommendations():
    client = MongoClient('localhost', 27017)
    db = client.yideas
    try:
        result = db.product_recommendations.delete_many({})
        for each in reco:
            recoThis = {}
            recoThis['product_id'] = each
            recoThis['recommendations'] = reco[each]
            db.product_recommendations.insert_one(recoThis);
    except Exception as e:
        traceback.print_exc()
        print e
    



class ContentEngine(object):

    SIMKEY = 'p:smlr:%s'
   
    
    
    def __init__(self):
        #self._r = redis.StrictRedis.from_url("'redis://localhost:6379'")
        pass

    def train(self, ds):
        self._train(ds)
        dumpRecommendations()


    def _train(self, ds):
        """
        Train the engine.

        Create a TF-IDF matrix of unigrams, bigrams, and trigrams for each product. The 'stop_words' param
        tells the TF-IDF module to ignore common english words like 'the', etc.

        Then we compute similarity between all products using SciKit Leanr's linear_kernel (which in this case is
        equivalent to cosine similarity).

        Iterate through each item's similar items and store the 100 most-similar. Stops at 100 because well...
        how many similar products do you really need to show?

        Similarities and their scores are stored in redis as a Sorted Set, with one set for each item.

        :param ds: A pandas dataset containing two fields: description & id
        :return: Nothin!
        """
        tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')
        tfidf_matrix = tf.fit_transform(ds['text'])

        cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

        for idx, row in ds.iterrows():
            similar_indices = cosine_similarities[idx].argsort()[:-100:-1]
            similar_items = [(cosine_similarities[idx][i], ds['product_id'][i]) for i in similar_indices]

            # First item is the item itself, so remove it.
            # This 'sum' is turns a list of tuples into a single tuple: [(1,2), (3,4)] -> (1,2,3,4)
            
            reco[row['product_id']] = list(map(lambda x: x[1], similar_items[1:]))
            print row['product_id'], reco[row['product_id']]
            flattened = sum(similar_items[1:], ())
            #self._r.zadd(self.SIMKEY % row['id'], *flattened)

    def predict(self, item_id, num):
        """
        Couldn't be simpler! Just retrieves the similar items and their 'score' from redis.

        :param item_id: string
        :param num: number of similar items to return
        :return: A list of lists like: [["19", 0.2203], ["494", 0.1693], ...]. The first item in each sub-list is
        the item ID and the second is the similarity score. Sorted by similarity score, descending.
        """
        return self._r.zrange(self.SIMKEY % item_id, 0, num-1, withscores=False, desc=True)
