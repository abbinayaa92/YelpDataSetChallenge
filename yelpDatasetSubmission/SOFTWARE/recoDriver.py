'''
Created on Dec 2, 2016

@author: Vansh-PC
'''
from pymongo import MongoClient
import pandas as pd
import engines
    

def loadProductDescriptions():
    client = MongoClient('localhost', 27017)
    db = client.yideas
    productDescriptions = db.product_descriptions
    productCursor = productDescriptions.find({})
    data =  pd.DataFrame(list(productCursor))
    return data
        


if __name__ == '__main__':
    allData = loadProductDescriptions()
    print allData
    content_engine = engines.ContentEngine()
    #content_engine.train('sample-data.csv')
    content_engine = content_engine.train(allData)