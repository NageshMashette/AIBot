import random
import json
import pickle
import numpy as np

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model


lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))
model = load_model('chat_model.h5')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words, show_details = True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i , word in enumerate(words):
            if word == w:
                bag[i]==1
                if show_details:
                    print("found in bag: %s" %word)
    return np.array(bag)

def predict_class(sentence, model):
    bow = bag_of_words(sentence, words, show_details=False)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i , r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x:x[1], reverse = True)
    return_list =[]
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag']== tag:
            result = random.choice(i['responses'])
            break
    return result

print("go! Bot is running")



def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = get_response(ints, intents)
    return res


'''
while True:
    message = input("")
    ints = predict_class(message)
    res = get_response(ints, intents)
    print(res)

'''
 #Flask code
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"about":"Homepage!"})

def decrypt(msg):
    string = msg
    new_string = string.replace("+", "")
    return new_string

@app.route('/home/<name>')
def hello_name (name):
    dec_msg = decrypt(name)
    response = chatbot_response(dec_msg)
    return response

if __name__ == '__main__':
    app.run(debug = True, threaded = False)
