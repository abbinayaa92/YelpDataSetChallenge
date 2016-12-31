from nltk.tokenize import RegexpTokenizer
# from stop_words import get_stop_words
# from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import gensim
from pymongo import MongoClient
import json
import io
import re

def generateLDAModel():
	client = MongoClient('localhost', 27017)
	db = client.yideas
	business = db.business
	reviews = db.cleanedReview
	db.topics.remove()
	reviewCursor = reviews.find({})

	# list for tokenized documents in loop
	texts = []

	# loop through document list
	for review in reviewCursor:
	    i = review['text']
	    tokens = getTokens(i)
	    # add tokens to list
	    texts.append(tokens)

	# turn our tokenized documents into a id <-> term dictionary
	dictionary = corpora.Dictionary(texts)
	 
	# convert tokenized documents into a document-term matrix
	corpus = [dictionary.doc2bow(text) for text in texts]

	# generate LDA model
	ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=50, id2word = dictionary, passes=20)
	topics =ldamodel.show_topics(num_topics=50, num_words=3, log=False, formatted=True)

	finalJsonOutput = []

	for topic in topics:
		topicId = topic[0]
		wordProbabilities = topic[1]
		wordProbs = wordProbabilities.split('+')
		topicWords = []
		topicWords.append(("topic_id",topicId))

		words = []
		for wp in wordProbs:
			wordProbSplit = wp.split('*')
			prob = wordProbSplit[0]
			word = wordProbSplit[1]
			word = word.strip(' ').strip('"')
			words.append(word)

		formattedList = ' '.join(words)
		
		topicWords.append(("words",formattedList))
		jsonOut = json.dumps(dict(topicWords))
		finalJsonOutput.append(jsonOut)
		db.topics.insert( json.loads( jsonOut ) )

	finalJson = "\n".join(finalJsonOutput)
	
	with open("topics.json","w") as f:
		f.write(finalJson)

	testModel(ldamodel, dictionary)


def testModel(ldamodel, dictionary):

	client = MongoClient('localhost', 27017)
	db = client.yideas
	business = db.business
	reviews = db.review
	reviewCursor = reviews.find({})

	productTopics = {}

	jsonOutput= []
	
	# loop through document list
	for review in reviewCursor:
		texts = []
		i = review['text']
		stars = review['stars']
		business = review['business_id']
		tokens = getTokens(i)
		texts.append(tokens)
		
		bow = dictionary.doc2bow(tokens)
		reviewId = review['review_id'];
		documentTopics = ldamodel[bow];

		reviewsTupleList = []
		reviewsTupleList.append(("review_id",reviewId))

		# documentTopics = ldamodel.get_document_topics(bow, minimum_probability=None, minimum_phi_value=None, per_word_topics=False)

		wordProbs = []
		for docTopic in documentTopics:
			doctopicid = docTopic[0]
			prob = docTopic[1]

			if(prob < 0.4):
				continue

			if business in productTopics.keys():
				prod_topics = productTopics[business]
				prod_topics.add(doctopicid)
				productTopics[business] = prod_topics
			else:
				productTopics[business] = set([doctopicid])

			# a = db.topics.find({'topic_id':doctopicid})

			# for pair in a:
			# 	words = pair['words']

			# 	tuples = []
			# 	tuples.append(("topic",words))
			# 	tuples.append(("prob", prob))

			# 	wordProbs.append(dict(tuples))

		# reviewsTupleList.append(("topicProbs", wordProbs))
		# reviewsTupleList.append(("stars", stars))
		# jsonOutput.append(json.dumps(dict(reviewsTupleList)))

		# finalJson = "\n".join(jsonOutput)
    
	# with open("out.json","w") as f:
	# 	f.write(finalJson)

	with open("productTopics.txt","w") as f:
		for x in productTopics.keys():
			tops = ' '.join([str(y) for y in productTopics[x]])
			row = x + ' ' + tops
			f.write(row + '\n')

def getTokens(i):

	tokenizer = RegexpTokenizer(r'\w+')
	# # create English stop words list
	# en_stop = get_stop_words('en')

	# # Create p_stemmer of class PorterStemmer
	# p_stemmer = PorterStemmer()
	# # clean and tokenize document string
	# raw = i.lower()
	tokens = tokenizer.tokenize(i)
	# remove stop words from tokens
	# stopped_tokens = [i for i in tokens if not i in en_stop]
	# # stem tokens
	# stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
	return tokens
	pass

if __name__ == '__main__':
    ldamodel = generateLDAModel()
