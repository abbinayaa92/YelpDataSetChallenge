import json;
from flask import Flask, url_for
from nltk.stem.porter import PorterStemmer
from pymongo import MongoClient;


client = MongoClient('localhost',27017);
db = client['yideas'];

businessCollection = db.business;
businessRatingCollection = db.businessRating;
modelMapCollection = db.modelMap;



app = Flask(__name__)
@app.route("/culturalTrends/<searchTerm>")
def culturalTrends( searchTerm ):

    data = {};
    states = [];
    stateobj = {};
    storedstates = set();

    state_short = {
        'AL': 0,'AK': 0,'AZ': 0,'AR': 0,'CA': 0,
        'CO': 0,'CT': 0,'DE': 0,'FL': 0,'GA': 0,
        'HI': 0,'ID': 0,'IL': 0,'IN': 0,'IA': 0,
        'KS': 0,'KY': 0,'LA': 0,'ME': 0,'MD': 0,
        'MA': 0,'MI': 0,'MN': 0,'MS': 0,'MO': 0,
        'MT': 0,'NE': 0,'NV': 0,'NH': 0,'NJ': 0,
        'NM': 0,'NY': 0,'NC': 0,'ND': 0,'OH': 0,
        'OK': 0,'OR': 0,'PA': 0,'RI': 0,'SC': 0,
        'SD': 0,'TN': 0,'TX': 0,'UT': 0,'VT': 0,
        'VA': 0,'WA': 0,'WV': 0,'WI': 0,'WY': 0,'DC':0,
    }

    statenames = {
        'AL': 'Alabama','AK': 'Alaska','AZ': 'Arizona','AR': 'Arkansas',
        'CA': 'California','CO': 'Colorado','CT': 'Connecticut',
        'DE': 'Delaware','FL': 'Florida','GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho','IL': 'Illinois','IN': 'Indiana',
        'IA': 'Iowa','KS': 'Kansas',
        'KY': 'Kentucky','LA': 'Louisiana','ME': 'Maine',
        'MD': 'Maryland', 'MA': 'Massachusetts',
        'MI': 'Michigan','MN': 'Minnesota',
        'MS': 'Mississippi','MO': 'Missouri',
        'MT': 'Montana','NE': 'Nebraska',
        'NV': 'Nevada','NH': 'New Hampshire',
        'NJ': 'New Jersey','NM': 'New Mexico',
        'NY': 'New York','NC': 'North Carolina',
        'ND': 'North Dakota','OH': 'Ohio',
        'OK': 'Oklahoma','OR': 'Oregon',
        'PA': 'Pennsylvania','RI': 'Rhode Island',
        'SC': 'South Carolina','SD': 'South Dakota',
        'TN': 'Tennessee','TX': 'Texas',
        'UT': 'Utah','VT': 'Vermont',
        'VA': 'Virginia','WA': 'Washington',
        'WV': 'West Virginia','WI': 'Wisconsin','WY': 'Wyoming',
        'DC': 'District of Columbia'
    }

    topfive = {}
    
    p_stemmer = PorterStemmer();
    searchTerm = p_stemmer.stem(searchTerm)
    print(searchTerm)

    for post in modelMapCollection.find():

        word = post["word"];

        if word == searchTerm:

            businesses = post["businesses"];

            for business in businesses:

                #get id of business
                id = business["id"]

                #search for business in business collection
                for biz in businessCollection.find():

                    bizid = biz["business_id"]
                    bizname = biz["name"]

                    if bizid == id:
                        address = biz["full_address"]
                        #print(address);
                        state_code = address.split(",")[-1];
                        #print(state_code);
                        state = state_code.split(" ")[1].strip();
                        break;

                        #print(state);

                if state not in statenames.keys():
                    break;

                rating = 0;
                #get rating for the business
                for biz in businessRatingCollection.find():
                    if biz["id"] == id:
                        rating = biz["rating"];
                        if state not in topfive.keys():

                            topfive[state] = [(bizname, rating)]

                        else:

                            bizlist = topfive[state]
                            bizlist.append((bizname, rating))
                            topfive[state] = bizlist
                        print(rating);
                        break;

                if state in state_short.keys():
                    state_short[state] = state_short[state] + rating;

                storedstates.add(statenames[state]);
            break;
                #stateobj["hits"] = rating;
                #stateobj["name"] = statenames[state];
                #states.append(stateobj);

    for key in statenames:
        if statenames[key] in storedstates:
            #continue;

            biz_state_list = topfive[key]
            biz_state_list.sort(key=lambda tup: tup[1])
            biz_state_list_five = [];
            for i in range(0,min(5,len(biz_state_list))):
                biz_state_list_five.append(biz_state_list[i])
            stateobj = {};
            stateobj["topfive"] = biz_state_list_five
            stateobj["hits"] = format(state_short[key], '.2f');
            stateobj["name"] = statenames[key];
            states.append(stateobj);
        else:
            stateobj = {};
            stateobj["hits"] = 0;
            stateobj["name"] = statenames[key];
            stateobj["topfive"] = [];
            states.append(stateobj);


    data['states'] = states;
    print(data);
    json_data = json.dumps(data)
    file_string = json_data;

    text_file = open("../Visualization/histograms_trial.js", "w")
    text_file.write(file_string);
    text_file.close()

    return file_string

#def main():
#culturalTrends("even")

if __name__ == "_main_":
    app.run(debug = True)


