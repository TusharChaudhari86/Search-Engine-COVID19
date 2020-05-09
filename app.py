from flask import Flask, render_template, jsonify, request, make_response
import pickle
from pymongo import MongoClient
from DataRequest.MakeApiRequests import Api
from flask_cors import CORS, cross_origin
import en_core_web_sm
import json
import pyrebase
import matplotlib.pyplot as plt




MONGODB_URI = 'mongodb://Tushar:tushar@cluster0-shard-00-00-jf2fj.mongodb.net:27017,cluster0-shard-00-01-jf2fj.mongodb.net:27017,cluster0-shard-00-02-jf2fj.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority'
cluster = MongoClient(MONGODB_URI)
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
    #articles = {"URL": articles['url'], "Title": articles['title'], "Body": articles['body_text'][0:500]}
    #articles = df.iloc[top, [11,5, 1]].reset_index(drop=True)
    #articles = [{"URL": articles.iloc[i,0], "Title": articles.iloc[i,1], "Body": articles.iloc[i,2][0:500]} for i in range(len(articles))]
    return render_template('search.html', articles=enumerate(articles), Question = query)


def processRequest(req):
    sessionID = req.get('responseId')
    result = req.get("queryResult")
    intent = result.get("intent").get('displayName')
    parameters = result.get("parameters")



    config = {
        "apiKey": "AIzaSyCkDXgXwFulPLFWizcAFmBfy-wkLbFsZ8Y",
        "authDomain": "cord-19-xmelda.firebaseapp.com",
        "databaseURL": "https://cord-19-xmelda.firebaseio.com",
        "projectId": "cord-19-xmelda",
        "storageBucket": "cord-19-xmelda.appspot.com",
        "messagingSenderId": "366698547823",
        "appId": "1:366698547823:web:fe0eaef288543eb2601b9a",
        "measurementId": "G-90KFJ64REE"
    }

    country = parameters.get("geo-country")
    api = Api()
    fulfillmentText, deaths_data, testsdone_data, date = api.makeApiRequestForCountry(country)

    total = fulfillmentText.get('total')
    deaths = deaths_data.get('total')
    recov = fulfillmentText.get('recovered')
    active = fulfillmentText.get('active')

    death_per = round(deaths * 100 / total, ndigits=1)
    active_per = round(active * 100 / total, ndigits=1)
    recov_per = round(recov * 100 / total, ndigits=1)

    labels = ['Active', 'recovered', 'Death']
    sizes = [active_per, recov_per, death_per]
    colors = ['dodgerblue', 'limegreen', 'red']
    table_data = [
        ["Total", total],
        ["Active", active],
        ["Recovered", recov],
        ["Deaths", deaths],
    ]

    fig, axs = plt.subplots(1, 2, constrained_layout=True)
    # pie
    axs[0].pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90, colors=colors)
    axs[0].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    # table
    axs[1].table(cellText=table_data, loc='center')
    axs[1].axis('off')

    fig.suptitle(country, fontsize=16)
    path_local = "Saved_images/" + country + ".png"
    plt.savefig(path_local, format="png")

    path_on_cloud = "images/" + country + ".png"

    firebase = pyrebase.initialize_app(config)
    storage = firebase.storage()

    imgurl = storage.child(path_on_cloud).put(path_local)

    img_url = storage.child(path_on_cloud).get_url(imgurl['downloadTokens'])

    if intent == 'covid_searchcountry':
        cust_country = parameters.get("geo-country")
        if(cust_country=="United States"):
            cust_country = "USA"

        fulfillmentText, deaths_data, testsdone_data, date = api.makeApiRequestForCountry(cust_country)
        yyyy,mm, dd = date[0:4], date[5:7], date[8:10]
        date = str(dd)+'-'+str(mm)+'-'+str(yyyy)
        webhookresponse = "As of date :" + date +"\n\n***Covid Report***\n\n" + " New cases :" + str(fulfillmentText.get('new')) + \
                          "\n" + " Active cases : " + str(
            fulfillmentText.get('active')) + "\n" + " Critical cases : " + str(fulfillmentText.get('critical')) + \
                          "\n" + " Recovered cases : " + str(
            fulfillmentText.get('recovered')) + "\n" + " Total cases : " + str(fulfillmentText.get('total')) + \
                          "\n" + " Total Deaths : " + str(deaths_data.get('total')) + "\n" + " New Deaths : " + str(
            deaths_data.get('new'))
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
    elif intent == 'Image':
        return {
    "fulfillmentMessages": [
        {
            "image": {
                "imageUri": "https://firebasestorage.googleapis.com/v0/b/cord-19-xmelda.appspot.com/o/images%2FIndia.png?alt=media&token=d3fb3087-1f0d-4ed9-ad86-d8e5c4308ca8"
            },
            "platform": "TELEGRAM"
        },
        {
            "text": {
                "text": [
                    ""
                ]
            }
        }
    ]
}

    else:
        return {
            "fulfillmentText": "something went wrong,Lets start from the begning, Say Hi",
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
