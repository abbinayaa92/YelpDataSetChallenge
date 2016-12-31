'''
Created on Dec 2, 2016

@author: Vansh-PC
'''
from pymongo import MongoClient
import traceback


def loadData():
    client = MongoClient('localhost', 27017)
    db = client.yideas
    #read from sample db only
    review_text = db.review_sample
    reviewCursor = review_text.find({})
    all = {}
    for each in reviewCursor:
        userid = each['user_id']     
        productId = each['business_id']
        if userid not in all:
            all[userid] = []
        all[userid].append(productId)
    return all



data = loadData()


def dumpUserProductMapper(data):
    client = MongoClient('localhost', 27017)
    db = client.yideas
    try:
        result = db.user_product.delete_many({})
        for each in data:
            userThis = {}
            userThis['user_id'] = each
            userThis['products'] = data[each]
            db.user_product.insert_one(userThis);
    except Exception as e:
        traceback.print_exc()
        print e

    


dumpUserProductMapper(data)