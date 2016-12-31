Before starting, ensure you cd to the SOFTWARE folder

How to install
1) The preprocessed data files and all other json files can be accessed at :
https://drive.google.com/drive/folders/0B_uS3RgQupwuTHZYYUVUVG02QWs?usp=sharing

Below are the list of json files present :
Original files provided by Yelp :
Yelp_academic_dataset_business.json
Yelp_academic_dataset_review.json
Yelp_academic_dataset_user.json

The preprocessed data file used for LDA and Sentiment Analysis
cleanedReview.json

Sentiment Analysis output files:
modelMap.json
modelMapSuper.json
businessRating.json
reviewRating.json

LDA output files:
user_product.json
product_recommendations.json
product_descriptions.json

2) DB Setup :
Install Mongo from https://docs.mongodb.com/master/administration/install-community/
	Steps to install using homebrew on mac :
	brew update
	brew install mongodb

3) Import json files
Commands :
mongoimport --db yideas --collection business --drop --file data/yelp_academic_dataset_business.json
mongoimport --db yideas --collection review --drop --file data/yelp_academic_dataset_review.json
mongoimport --db yideas --collection user --drop --file data/yelp_academic_dataset_user.jsonmongoimport --db yideas --collection user_product --drop --file data/user_product.json
mongoimport --db yideas --collection product_recommendations --drop --file data/product_recommendations.json
mongoimport --db yideas --collection product_descriptions --drop --file data/product_descriptions.json
mongoimport --db yideas --collection cleanedReview --drop --file data/cleanedReview.json
mongoimport --db yideas --collection modelMap --drop --file data/modelMap.json
mongoimport --db yideas --collection modelMap --drop --file data/modelMapSuper.json
mongoimport --db yideas --collection reviewRating --drop --file data/reviewRating.json
mongoimport --db yideas --collection businesRating --drop --file data/businessRating.json

4) Install and enable CORS plugin on Google Chrome

----Optional--- 
Steps 5 and 6 are optional as the json files above are the pre-processed output files from LDA and Classification algorithms. The following commands were used to generate the output of the algorithms and insert into the database.

5) 
Install python libraries
pip3 install flask
pip3 install gensim
pip3 install nltk.download(“stopwords”)
pip install pymongo
pip install numpy
pip install stemming

6) Run the following python commands to initialize backend:
python3 DataClean.py
python3 generateTopics.py
python classifier.py
python recoDriver.py



How to run the demo:

Run the following commands from console 
mongod --httpinterface --rest
python -m SimpleHTTPServer 8080 from the dashboard folder

From the dashboard/reco/CulturalTrends folder, run the following 
export FLASK_APP=CulturalTrends.py
flask run

Ensure you have enabled CORS plugin on chrome
Run http://localhost:8080/reco/ on  Google Chrome



How to use Yideas:
All these steps have been recorded in a video for your convenience. This video is located at DOC/Yideas.mp4 

Once you run the app, you will see a dashboard with a left sidepanel.
There are 3 main components of our app:
	Login to view personalized recommendations on the main dashboard
	User name: Eddie, User ID: Qh5A5NlP4UVvddSasOYR4A, password: 1234
	The dashboard will show products that Eddie has reviewed and those that are recommended for him

Normalized product and review ratings based on Sentiment Analysis of Reviews
	Click on Review Analysis on the left panel of the main dashboard
	You will see a drop down list of products where the you can search for any product.
	On selecting a product, you can view all words associated with respective reviews for the product as well as the sentiment of each word. The size of the bubbles corresponds to frequency of the word and the color indicates negative/positive sentiment. 
	On clicking each word bubble, reviews associated with the word and their normalized ratings are displayed.
	The normalised rating for the restaurant is also displayed

Cultural Trends Analysis
	On the left panel of the dashboard, click on Trends
	Type in a keyword, say, Indian. This represents the cultural trend you want to search on. Click on search.
	After a minute, you will see a heatmap of USA with varying shades of color depicting popularity of the trend “indian” in different states, with darker color indicating most popular.
	On hovering over the state, you can see the sentiment value of the search term in each state 
	You can also  zoom into a particular state to see the top 5 businesses for that trend.
