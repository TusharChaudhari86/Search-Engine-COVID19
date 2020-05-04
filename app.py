from flask import Flask, render_template, jsonify, request
import pickle
from pymongo import MongoClient

cluster = MongoClient("mongodb://Tushar:tushar@cluster0-shard-00-00-jf2fj.mongodb.net:27017,cluster0-shard-00-01-jf2fj.mongodb.net:27017,cluster0-shard-00-02-jf2fj.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
db = cluster['research-paper']
collection = db['covid']

import en_core_web_sm

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
    return render_template('index.html', articles=articles, Question = query)

if __name__ == "__main__":
    app.run(debug=True)
