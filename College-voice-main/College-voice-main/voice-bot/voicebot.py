
import random 
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.python.keras.models import load_model
#import pyttsx3
#import speech_recognition as sr
#r = sr.Recognizer()
#engine=pyttsx3.init()
#voices = engine.getProperty("voices")
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
lemmatizer=WordNetLemmatizer()
intents=json.loads(open('./voice-bot/intents.json').read())
words=pickle.load(open('./voice-bot/words.pk1','rb'))
classes=pickle.load(open('./voice-bot/classes.pk1','rb'))
model = load_model('./voice-bot/voicebot_model.h5')
"""
def speaknow(res):
    engine.say(res)
    engine.setProperty("voice", voices[0].id)
    engine.setProperty('rate',150)
    engine.setProperty('volume',0.7)
    engine.runAndWait()
    engine.stop()
"""
def clean_up_sentence(sentence):
    sentence_words=nltk.word_tokenize(sentence)
    sentence_words=[lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words
def bag_of_words(sentence):
    sentence_words=clean_up_sentence(sentence)
    bag=[0]*len(words)
    for w in sentence_words:
        for i,word in enumerate(words):
            if word==w:
                bag[i]=1
    return np.array(bag)
def predict_class(sentence):
    bow=bag_of_words(sentence)
    res=model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD=0.25
    results=[[i,r]for i,r in enumerate(res) if r> ERROR_THRESHOLD]
    results.sort(key=lambda x:x[1],reverse=True)
    return_list=[]
    for r in results:
        return_list.append({'intent':classes[r[0]],'probability':str(r[1])})
    return return_list
def get_responses(intents_list,intents_json):
    tag=intents_list[0]['intent']
    list_of_intents=intents_json['intents']
    for i in list_of_intents:
        if i['tag']==tag:
            result=random.choice(i['responses'])
            break
    return result


print(" Bot is running ")
"""
def voice():
    with sr.Microphone() as source:
    #print('Speak Anything :')
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print('You said : {}'.format(text))
        return text

    except:
        print('Sorry could not recgnize your voice')   
 """
def send_message(message):
    #message = input("")
    ints = predict_class(message)
    res = get_responses(ints, intents)
    #abc=voice()
    #if abc != " ":
        ##ints=predict_class(abc)
        #res = get_responses(ints,intents)
    #speaknow(res)
    return res

   
    #speaknow(res)
    #print(res)
    
