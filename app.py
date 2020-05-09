from flask import Flask, render_template, jsonify, request, make_response
import pickle
from pymongo import MongoClient
from DataRequest.MakeApiRequests import Api
from flask_cors import CORS, cross_origin
import en_core_web_sm
import json

cluster = MongoClient("mongodb://Tushar:tushar@cluster0-shard-00-00-jf2fj.mongodb.net:27017,cluster0-shard-00-01-jf2fj.mongodb.net:27017,cluster0-shard-00-02-jf2fj.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
db = cluster['research-paper']
collection = db['covid']


app = Flask(__name__)

# medium model
nlp = en_core_web_sm.load(disable=["tagger", "parser", "ner"])
nlp.max_length = 2000000

bm25 = pickle.load(open('database.pkl', 'rb'))

def spacy_tokenizer(sentence):
    return [word.lemma_ for word in nlp(sentence) if not (word.like_num or word.is_stop or word.is_punct or word.is_space or len(word)==1)]

def Sort_Tuple(tup):
    tup.sort(key = lambda x: x[1],  reverse = True)
    return tup


@app.route('/')
def Home():

    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = str(request.form['text'])

    #create token query
    tokenized_query = spacy_tokenizer(query)

    #get the score of querying for each observation
    doc_scores = bm25.get_scores(tokenized_query)

    #Sorted scores
    scores = [(idx, scr) for idx, scr in enumerate(doc_scores)]

    #get top 10 scores
    top = [tup[0] for tup in Sort_Tuple(scores)[0:10]]
    articles = []
    for index in top:
        articles.append(collection.find_one({'index': index}))
    return render_template('search.html', articles=enumerate(articles), Question = query)


# processing the request from dialogflow
def processRequest(req):
    sessionID = req.get('responseId')
    result = req.get("queryResult")
    intent = result.get("intent").get('displayName')
    query_text = result.get("queryText")
    parameters = result.get("parameters")

    api = Api()
    if intent == 'covid_searchcountry':
        cust_country = parameters.get("geo-country")
        if(cust_country=="United States"):
            cust_country = "USA"

        fulfillmentText, deaths_data, testsdone_data, date = api.makeApiRequestForCountry(cust_country)
        yyyy,mm, dd = date[0:4], date[5:7], date[8:10]
        date = str(dd)+'-'+str(mm)+'-'+str(yyyy)
        webhookresponse = "Date :" + date +"\n***Covid Report***\n\n" + " New cases :" + str(fulfillmentText.get('new')) + \
                          "\n" + " Active cases : " + str(
            fulfillmentText.get('active')) + "\n" + " Critical cases : " + str(fulfillmentText.get('critical')) + \
                          "\n" + " Recovered cases : " + str(
            fulfillmentText.get('recovered')) + "\n" + " Total cases : " + str(fulfillmentText.get('total')) + \
                          "\n" + " Total Deaths : " + str(deaths_data.get('total')) + "\n" + " New Deaths : " + str(
            deaths_data.get('new')) + \
                          "\n" + " Total Test Done : " + str(deaths_data.get('total')) + "\n\n*******END********* \n "
        print(webhookresponse)

        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhookresponse
                        ]

                    }
                }
            ]
        }
    
    elif intent == "Welcome" or intent == "continue_conversation" or intent == "not_send_email" or intent == "endConversation" or intent == "Fallback" or intent == "covid_faq" or intent == "select_country_option":
        fulfillmentText = result.get("fulfillmentText")

    else:
        return {
            "fulfillmentText": "something went wrong,Lets start from the begining, Say Hi",
        }

@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():
    req = request.get_json(silent=True, force=True)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


if __name__ == "__main__":
    app.run(debug=False)
