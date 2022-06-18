#test_cap

import pandas as pd
import numpy as np
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
import requests

#pour désactiver l'avertissement de dépréciation, exécutez 'pytest --disable-warnings' en ligne de commande.

#variables
app_name = 'luis_train_pred120'
predictionKey = '1f40e3ea26524ae5b2d3fae9da451fd4'
predictionEndpoint = 'https://luistrainval.cognitiveservices.azure.com/'
app_id = '9551a6aa-e958-4e58-8d10-2abe1eb4b4de'
response_get_endpoint = 'https://westeurope.api.cognitive.microsoft.com/luis/v2.0/apps/9551a6aa-e958-4e58-8d10-2abe1eb4b4de'
data_path = "tests/data/frames.json"

#Préparez un test sur la classe qui est utilisée dans le chatbot.
class BookingDetails:
    def __init__(
        self,
        dst_city: str = None,
        or_city: str = None,
        str_date: str = None,
        end_date: str = None,
        budget: str = None,
    ):
        self.dst_city: str = dst_city
        self.or_city: str = or_city
        self.str_date: str = str_date
        self.end_date: str = end_date
        self.budget: str = budget
        

def test_flight_or_city():
    assert BookingDetails(or_city='Paris').or_city == 'Paris'

def test_flight_dst_city():
    assert BookingDetails(str_date='august 1').str_date == 'august 1'

def test_flight_budget():
    assert BookingDetails(budget=500).budget == 500

#effectuer un test sur l'aspect extraction de données de la fonction de transformation des données
def clean_split_data(data_path):
    """ Le chemin des données brutes est la fonction arg. Cette fonction importe le fichier JSON de Frames:
    a) nettoie les données, b) extrait la première interaction de l'utilisateur. 
    c) crée df sur les 5 éléments attendus pour les entités. d) forme/teste la division.
    """
    raw_data = pd.read_json(data_path)
    raw_data[["userSurveyRating", "wizardSurveyTaskSuccessful"]] = [[j["userSurveyRating"], j["wizardSurveyTaskSuccessful"]] for j in raw_data.labels]
    raw_data.drop('labels', axis=1, inplace=True)
    raw_data.dropna(axis=0, how='any', inplace=True)
    #inclure uniquement les interactions les mieux notées par les utilisateurs pour la formation de luis
    cleaned_data = raw_data[raw_data['userSurveyRating'] >= 4]
    cleaned_data.reset_index(drop=True, inplace=True)
    # Create an empty list to save the result
    list_for_df = []
    # iter à travers la ligne des tours de colonne
    for turn in cleaned_data['turns']:
        # Create an empty dictionary
        diction_for_list = {}
        # mettre le texte de l'utilisateur dans le dictionnaire
        diction_for_list.update({'text':turn[0].get('text')})
        #accéder aux labels>acts pour pouvoir toucher les args nichés
        for segment in turn[0].get('labels').get('acts'):
            #boucle sur les arguments dans arg
            for argument in segment.get('args'):
            #mettre les paires clé:val dans le dictionnaire
                diction_for_list.update({argument.get('key'):argument.get('val')})
        list_for_df.append(diction_for_list)
        return list_for_df

test_list = [{'text': "I'd like to book a trip to Atlantis from Caprica on Saturday, August 13, 2016 for 8 adults. I have a tight budget of 1700.",
  'intent': 'book',
  'dst_city': 'Atlantis',
  'or_city': 'Caprica',
  'str_date': 'Saturday, August 13, 2016',
  'n_adults': '8',
  'budget': '1700'}]

def test_clean_split_data():
    assert clean_split_data(data_path) == test_list

#Effectuer un test sur la fonction qui fait une requête luis et retourne l'intention de la requête.
runtimeCredentials = CognitiveServicesCredentials(predictionKey)
clientRuntime = LUISRuntimeClient(endpoint=predictionEndpoint, credentials=runtimeCredentials)
 
def luis_prediction(clientRuntime, app_id):
    """tester 1 requête du modèle de Luis"""
    text_request = {'query':'I would like to travel to london from paris on august 18 and return on august 25 for a budget of 1000 euros'}
    luis_prediction_response = clientRuntime.prediction.resolve(app_id, query=text_request, verbose=True)

    text_returned = luis_prediction_response.query
    top_intent = luis_prediction_response.top_scoring_intent.intent
    intents = luis_prediction_response.intents
    entities = luis_prediction_response.entities
    return top_intent

def test_luis_prediction():
    assert luis_prediction(clientRuntime, app_id) == 'BookFlight'

#Effectuer un test sur la fonction qui cqlculte la précision de validation de l'intention.
val_utterance = [{"text": "ay whats up?", "intent": "BookFlight", "entities": []}, {"text": "yeah, i'm looking for an 8 day trip for the family.", "intent": "BookFlight", "entities": []}, {"text": "the most important meeting of my life is taking place in monterrey. do you fly to monterrey from manas?", "intent": "BookFlight", "entities": [{"entity": "or_city", "startPos": 97, "endPos": 101}, {"entity": "dst_city", "startPos": 57, "endPos": 65}]}]
def get_results_validation(predictionKey, response_get_endpoint, val_utterance):
    results_validation = []
    for text in val_utterance:
        text = text['text']
        #text_list.append(text)
        params = {"q": text, "subscription-key" : predictionKey}
        url_1 = response_get_endpoint
        response_status = requests.get(url_1, params=params )
        results_validation.append(response_status.json())
    print ('Getting validation response:')
    print (response_status)
    return results_validation

results_validation = get_results_validation(predictionKey, response_get_endpoint, val_utterance)
val_df_whole = pd.read_csv('tests/data/val_df.csv')
val_df = val_df_whole.iloc[0:3]

def get_validation_intent_accuracy(results_validation, val_df):
    #pd.set_option('display.max_rows', None)
    pred_intent = []
    for dictionaries in results_validation:
        pred_intent_values = (dictionaries['topScoringIntent']['intent'])
        pred_intent.append(pred_intent_values)
    df_pred_intent = pd.DataFrame (pred_intent, columns = ['pred_intent'])
    val_df.reset_index(drop=True, inplace=True)
    gt_intent_series = val_df.intent
    gt_intent_df = pd.DataFrame(gt_intent_series)
    gt_intent_df.rename(columns={"intent":"gt_intent"}, inplace = True)
    all_intents = pd.concat([df_pred_intent, gt_intent_df], axis=1)
    correct_intents = 0
    for index in range(len(all_intents)):
        #print (index)
        if (all_intents['pred_intent'].iloc[index] == 'BookFlight') & (all_intents['gt_intent'].iloc[index] == 'BookFlight'):
            correct_intents += 1
        if (all_intents['pred_intent'].iloc[index] == 'Cancel') & (all_intents['gt_intent'].iloc[index] == 'Cancel'):
            correct_intents += 1
        if (all_intents['pred_intent'].iloc[index] == 'None') & (all_intents['gt_intent'].iloc[index] == 'None'):
            correct_intents += 1
    accuracy_percent = correct_intents/len(all_intents)*100
    return accuracy_percent

def test_get_validation_intent_accuracy():
    assert get_validation_intent_accuracy(results_validation, val_df) == 100.0
