#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
from __future__ import division
import json
import traceback
import random

from decimal import *
import sys
from pymongo import MongoClient
import matplotlib.pyplot as plt
import math
import numpy
import random
'''
Created on Nov 10, 2016

@author: Vansh-PC
'''
FILENAME = "/Users/Vansh-PC/Downloads/yelp_dataset_challenge_academic_dataset/review_sample.json"
MODEL_OUT = "modelMap.csv"
SEMANTIC_OUT = "semantic.csv"
TRAINING_THRESHOLD = 0.9
POSITIVE_THRESHOLD = 2.5
POSITIVE = "positive"
NEGATIVE = "negative"
positiveCount = 'positiveCount'
negativeCount = 'negativeCount'
positiveProb = 'positiveProb'
negativeProb = 'negativeProb' 
reviewList = 'reviewList'
reviewId = 'reviewId'
label = 'label'
actualLabel = 'actual'
actualRating = 'stars'
resultPositive = 'resultPositive'
resultNegative = 'resultNegative'


def translatePositive(value, leftMin, leftMax, rightMin, rightMax, mean, std):
    if value <= (mean - 5 *std):
        return 2.5
    elif value <= (mean - 3 * std):
        return 3
    elif value >= (mean - 2 * std) and value < (mean + 1 * std):
        return 3.4
    elif value >= (mean + 1 * std) and value < (mean + 1.5 * std):
        return 3.8
    elif value >= (mean + 1.5 * std) and value < (mean + 3 * std):
        return 4.2
    elif value >= (mean + 3 * std) and value < (mean + 5 * std):
        return 4.6
    else:
        return rightMax
    
def translateNegative(value, leftMin, leftMax, rightMin, rightMax, mean, std):
    if value <= (mean - 1 *std):
        return 0.5
    elif value <= (mean - 0.5 * std):
        return 1.2
    elif value >= mean and value < (mean + 3 * std):
        return 1.8
    else:
        return 2.5




def loadData(FILENAME):
    client = MongoClient('localhost', 27017)
    db = client.yideas
    # read from sample db only
    review_text = db.cleanedReview
    reviewCursor = review_text.find({}).limit(100000)
    #reviewCursor = review_text.find({"date": {'$gte':'2014-01-01','$lt':'2014-12-01'}})

    all = []
    for each in reviewCursor:
        # #print each
        data = each  # current_line = correct_sentence(removePunctuation(data['text'].lower())).split(' ')
        # current_line = removePunctuation(data['text'].lower()).split(' ')
        # current_line = [word for word in current_line if word not in cachedStopWords]
        # print  data['business_id'],data['review_id'] , current_line
        current_line = data['text'].split()
        all.append((current_line, data['stars'], data['review_id'], data['business_id']))
    return all
    # maxSize = 100000
    # all = []
    # indices = numpy.random.choice(2500000,100000,replace=False)
    # for i in indices:
    #     #i = random.randrange(2500000)
    #     data = reviewCursor[i]
    #     current_line = data['text'].split()
    #     all.append((current_line, data['stars'], data['review_id'], data['business_id']))
    # return all

    # for each in reviewCursor:
    #         # #print each
    #         data = each  #             current_line = correct_sentence(removePunctuation(data['text'].lower())).split(' ')
    #         #current_line = removePunctuation(data['text'].lower()).split(' ')
    #         # current_line = [word for word in current_line if word not in cachedStopWords]
    #         # print  data['business_id'],data['review_id'] , current_line
    #         current_line = data['text'].split()
    #         all.append((current_line, data['stars'], data['review_id'], data['business_id']))
    # random.shuffle(all)
    # return all[0:maxSize]
        

def splitData(allData, TRAINING_THRESHOLD):
    random.shuffle(allData)
    cutOff = int(TRAINING_THRESHOLD * len(allData))
    return allData[:cutOff], allData[cutOff:]


def normalizeModelMap(modelMap):
    allPos, allNeg = Decimal(0), Decimal(0)
    for each in modelMap:
        modelMap[each][positiveProb] = Decimal(modelMap[each][positiveCount]) / Decimal(modelMap[each][positiveCount] + modelMap[each][negativeCount])
        modelMap[each][negativeProb] = Decimal(1.0) - modelMap[each][positiveProb]
        


def updateModelMap(modelMap, allWords, sentiment, reviewId, positive_examples, negative_examples):
    allPos = 0.0
    allNeg = 0.0
    for word in allWords:
        if not (word in modelMap):
            modelMap[word] = {positiveCount:0, negativeCount:0, positiveProb:0, negativeProb:0, reviewList:set()}
        if POSITIVE == sentiment:
            modelMap[word][positiveCount] += (modelMap[word][positiveCount] + 1)
            modelMap[word][reviewList].add(reviewId)
        else:
            modelMap[word][negativeCount] += (modelMap[word][negativeCount] + 1)
            modelMap[word][reviewList].add(reviewId)
            
    

def buildModel(trainingSet, positive_words, negative_words):
    modelMap = {}
    for each in trainingSet:
        updateModelMap(modelMap, each[0], each[1], each[2], positive_words, negative_words)
    normalizeModelMap(modelMap)
    return modelMap


def addLabelsAndBuildModel(train, POSITIVE_THRESHOLD):
    positive = []
    negative = []
    positiveWords = 0.0
    negativeWords = 0.0
    wordBusinessMap = {}  # word => business => count of word and holds a set of review Id's
    # this is denormalized but really what we want   
    for each in train:
        freqMap = {}
        for word in each[0]:
            word = word.strip()
            if word not in freqMap:
                freqMap[word] = 0
            freqMap[word] = freqMap[word] + 1
        
#         for eachWord in freqMap:
#             if each[2] =='V-bqYx62zpxfH2oFkzXPzw' :
#                 print  each[3], each[2], eachWord, freqMap[word]
#         
        for word in freqMap:
            if word not in wordBusinessMap:
                wordBusinessMap[word] = {}
            if each[3] not in wordBusinessMap[word]:
                wordBusinessMap[word][each[3]] = {'reviews':set(), 'frequency':0, 'id':each[3], 'freq' : [], 'uniqueReviewCount':0}
                wordBusinessMap[word][each[3]]['frequency'] = freqMap[word]
                
            else:
                wordBusinessMap[word][each[3]]['frequency'] += freqMap[word] 
            wordBusinessMap[word][each[3]]['reviews'].add(each[2])
            wordBusinessMap[word][each[3]]['freq'].append((each[2], freqMap[word]))
            wordBusinessMap[word][each[3]]['uniqueReviewCount'] = len(wordBusinessMap[word][each[3]]['reviews'])
        
            
                
        if float(each[1]) > POSITIVE_THRESHOLD:
            positive.append((each[0], 'positive', each[2], each[3]))
            positiveWords += len(each[0])
        else:
            negative.append((each[0], 'negative', each[2], each[3]))
            negativeWords += len(each[0])
    for each in wordBusinessMap:
            for eachBusiness in wordBusinessMap[each]:
                wordBusinessMap[each][eachBusiness]['reviews'] = list(wordBusinessMap[each][eachBusiness]['reviews'])
    # print wordBusinessMap    
    trainingSet = positive + negative
    # #print positiveWords, negativeWords
    modelMap = buildModel(trainingSet, positiveWords, negativeWords)
    for each in wordBusinessMap:
        modelMap[each]['businesses'] = wordBusinessMap[each]
    # print modelMap
    # print '************************************************'
   
    # float(len(positive))/len(trainingSet),float(len(negative))/len(trainingSet) 
    return trainingSet, modelMap, (len(positive) / (len(positive) + len(negative))), (len(negative) / (len(positive) + len(negative)))

def addLabels(train, POSITIVE_THRESHOLD):
    positive = []
    negative = []   
    for each in train:
        if float(each[1]) > POSITIVE_THRESHOLD:
            positive.append((each[0], POSITIVE, each[2]))
        else:
            negative.append((each[0], NEGATIVE, each[2]))
    trainingSet = positive + negative
    return trainingSet
    

def getMeanAndStd(l):
    arr = numpy.array(l)
    return arr.mean(), arr.std()


def classify(test, modelMap, positiveProbailityOverall, negativeProbabilityOverall):
    testResult = {}
    wrongLabels = 0
    minPos, maxPos = (1.0), (1.0)
    minNegative, maxNegative = (1.0), (1.0)
    
    positiveVals = []
    negativeVals = []
     
    posExpectedPos = 0.0
    posExpectedNeg = 0.0
    negExpectedNeg = 0.0
    negExpectedPos = 0.0
    
    for eachReview in test:
        testResult[eachReview[2]] = {}
        testResult[eachReview[2]][reviewId] = eachReview[2]
        testResult[eachReview[2]]['busiessId'] = eachReview[3]
        positiveInit = (1.0)
        negativeInit = (1.0)
        valueOne = Decimal(1.0)

        for eachWord in eachReview[0]:
            if eachWord in modelMap:
                if modelMap[eachWord][positiveCount] != 0:  # * 100000000000000000000000000000000000000
                    positiveInit = positiveInit + float((valueOne + modelMap[eachWord][positiveProb]).log10()) + math.log(1 + positiveProbailityOverall)
                if modelMap[eachWord][negativeCount] != 0:
                    negativeInit = negativeInit + float((valueOne + modelMap[eachWord][negativeProb]).log10()) + math.log(1 + negativeProbabilityOverall)
                
#                 if modelMap[eachWord][positiveCount]!=0:
#                     positiveInit = positiveInit * modelMap[eachWord][positiveCount] * (positiveProbailityOverall) * 100
#                 if modelMap[eachWord][negativeCount]!=0:
#                     negativeInit = negativeInit * modelMap[eachWord][negativeCount] * (negativeProbabilityOverall) * 100
        if positiveInit > negativeInit:
            testResult[eachReview[2]][label] = POSITIVE
            testResult[eachReview[2]]['score'] = positiveInit
            positiveVals.append(positiveInit)
            if (positiveInit > maxPos):
                maxPos = positiveInit
            if positiveInit < minPos:
                minPos = positiveInit
        else:
            testResult[eachReview[2]][label] = NEGATIVE
            testResult[eachReview[2]]['score'] = negativeInit
            if (negativeInit > maxNegative):
                maxNegative = negativeInit
            if (negativeInit < minNegative):
                minNegative = negativeInit
            negativeVals.append(negativeInit)
            
        # testResult[eachReview[2]][resultPositive] = positiveInit/(positiveInit + negativeInit)
        # testResult[eachReview[2]][resultNegative] = 1 - testResult[eachReview[2]][resultPositive] 
        # comment this for real world learning
        testResult[eachReview[2]][actualRating] = eachReview[1] 
        if float(eachReview[1]) >= POSITIVE_THRESHOLD:
            expectedLabel = POSITIVE
        else:
            expectedLabel = NEGATIVE
        testResult[eachReview[2]][actualLabel] = expectedLabel
        testResult[eachReview[2]]["expected"] = expectedLabel
        if testResult[eachReview[2]][label] == POSITIVE:
            if testResult[eachReview[2]]["expected"] == POSITIVE:
                posExpectedPos += 1
            else:
                posExpectedNeg += 1
        else:
            if testResult[eachReview[2]]["expected"] == NEGATIVE:
                negExpectedNeg += 1
            else:
                negExpectedPos += 1
        if testResult[eachReview[2]][label] != expectedLabel:
            wrongLabels += 1
    
    accuracy = (float(len(test) - wrongLabels) / len(test)) * 100.0
    print "positive expected pos: ", posExpectedPos
    print "positive expected neg: ", posExpectedNeg
    print "neg expected neg: ", negExpectedNeg
    print "neg expected Pos: ", negExpectedPos
#     
    positiveMean, positiveStd = getMeanAndStd(positiveVals)
    negativeMean, negativeStd = getMeanAndStd(negativeVals)
#     print positiveMean, positiveStd
#     print negativeMean, negativeStd
    return testResult, accuracy, maxPos, minPos, maxNegative, minNegative, positiveMean, positiveStd, negativeMean, negativeStd
        

        
def dumpModelMap(modelMap, businessReviewRating, reviewRating):
    try:
        client = MongoClient('localhost', 27017)
        db = client.yideas
        result = db.businessRating.delete_many({})
        result = db.reviewRating.delete_many({})
        result = db.modelMap.delete_many({})
        result = db.modelMapSuper.delete_many({})
        model_super = []
        reviews_ = []
        modelmap_ = []
        business_ = []
        for each in reviewRating:
            reviewThis = {}
            reviewThis['id'] = each
            reviewThis['rating'] = reviewRating[each]
            reviews_.append(reviewThis)
            
        for each in businessReviewRating:
            reviewThis = {}
            reviewThis['id'] = each
            reviewThis['rating'] = businessReviewRating[each]['rating']
            business_.append(reviewThis)
            
        for each in modelMap:
            model = {}
            model['word'] = each
            # model['countOverall'] = float(modelMap[each][negativeCount] + modelMap[each][positiveCount])
            model['positiveProbability'] = float(modelMap[each][positiveProb])
            model['negativeProbability'] = float(modelMap[each][negativeProb])


            model['businesses'] = modelMap[each]['businesses'].values()
            for eachBusiness in  modelMap[each]['businesses']:
                modelSuper = {}
                modelSuper['word'] = each
                modelSuper['positiveProbability'] = float(modelMap[each][positiveProb])
                modelSuper['negativeProbability'] = float(modelMap[each][negativeProb])
                modelSuper['business'] = modelMap[each]['businesses'][eachBusiness]
                #modelSuper[modelMap[each]['businesses'][eachBusiness]['id']] = modelMap[each]['businesses'][eachBusiness]['id']
                model_super.append(modelSuper)
            modelmap_.append(model)
            
        db.modelMapSuper.insert_many(model_super)
        db.reviewRating.insert_many(reviews_)
        db.businessRating.insert_many(business_);
        db.modelMap.insert_many(modelmap_)
        
    except Exception as e:
        traceback.print_exc()
        print e
    
#     with open(MODEL_OUT, "w") as f:
#         for each in modelMap:
#             try:
#                 reviewsAll = ",".join(modelMap[each][reviewList])
#                 reviewsAll = '"' +  '[' + reviewsAll + ']"'
#                 ##print  reviewsAll
#                 f.write(str(each) + "," + str(modelMap[each][negativeCount] + modelMap[each][positiveCount]) + "," + str(modelMap[each][positiveProb]) + "," + str(modelMap[each][negativeProb]) + "," + str(reviewsAll) + "\n") 
#             except Exception as e:
#                 ##print e
#                 pass


def assignRatings(testResult, maxPos, minPos, maxNegative, minNegative, positiveMean, positiveStd, negativeMean, negativeStd):
    reviewRating = {}
    businessRating = {}
    all = []
    for each in testResult:
        if testResult[each]['busiessId'] not in businessRating:
            businessRating[testResult[each]['busiessId']] = {'score':[], 'rating':0.0}
            
        if testResult[each][label] == POSITIVE:
            rating = translatePositive(testResult[each]['score'], minPos, maxPos, (2.0), (5.0), positiveMean, positiveStd)
            # rating = translate(testResult[each]['score'], -math.log(maxPos), -math.log(minPos), Decimal(3.0), Decimal(5.0))
        else:
            rating = translateNegative(testResult[each]['score'], minNegative, maxNegative, (0.5), (2.0), negativeMean, negativeStd)
            # rating = translate(testResult[each]['score'], -math.log(maxNegative), -math.log(minNegative), Decimal(3.0), Decimal(5.0))
        reviewRating[each] = 3.0
        all.append(rating)
        try:
            # print rating
            reviewRating[each] = float(rating)
        except Exception as e:
            print rating
            print "Exception in converting rating"
            traceback.print_exc()
            print e
        businessRating[testResult[each]['busiessId']]['score'].append(reviewRating[each])
        
    # print reviewRating
    b = []
    for each in businessRating:
        businessRating[each]['rating'] = sum(businessRating[each]['score']) / float(len(businessRating[each]['score'])) 
        b.append(businessRating[each]['rating'])
    # print businessRating
#     plt.plot(all)
#     plt.show()
#     plt.plot(b)
#     plt.show()
    return businessRating, reviewRating
    
    
if __name__ == '__main__':
    allData = loadData(FILENAME)
    print "Loaded the data"
    trainInit, test = splitData(allData, TRAINING_THRESHOLD)
    "print splitted into testing and training"
    train, modelMap, positiveProbailityOverall, negativeProbabilityOverall = addLabelsAndBuildModel(trainInit, POSITIVE_THRESHOLD)
    # sanity check
    #===========================================================================
    # for each in modelMap:
    #     if modelMap[each][positiveProb]!= 0 and modelMap[each][positiveProb]!=1:
    #         #print each,  modelMap[each]
    #===========================================================================
    print "Built model"
    testResult, accuracy, maxPos, minPos, maxNegative, minNegative, positiveMean, positiveStd, negativeMean, negativeStd = classify(test + trainInit, modelMap, positiveProbailityOverall, negativeProbabilityOverall)
    print "Classified data"
    print accuracy
    
#     with open(SEMANTIC_OUT, "w") as g:
#         for each in testResult:
#             g.write(testResult[each][reviewId] + "," + testResult[each][label] + "," + testResult[each]["expected"] + "\n")
#     
    # testResult, accuracy = classify(trainInit, modelMap, positiveProbailityOverall, negativeProbabilityOverall)
    # #print accuracy
    businessReviewRating, reviewRating = assignRatings(testResult, maxPos, minPos, maxNegative, minNegative, positiveMean, positiveStd, negativeMean, negativeStd)
    print "Assigned ratings"
    dumpModelMap(modelMap, businessReviewRating, reviewRating)
    print "completed dumping "
    # santity check
    #===========================================================================
    # for each in testResult:
    #     #print each, testResult[each]
    #===========================================================================
    
