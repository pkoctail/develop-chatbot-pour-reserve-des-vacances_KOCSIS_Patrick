import pandas as pd
import numpy as np
import time
import json

# from sklearn.model_selection import train_test_split
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.language.luis.authoring.models import (
    ApplicationCreateObject,
)
import requests
import luis_functions

# variables
authoringKey = "602b1a1c4a354e618dc97c8eddcb217d"
authoringEndpoint = "https://luistrainval-authoring.cognitiveservices.azure.com/"
predictionKey = "1f40e3ea26524ae5b2d3fae9da451fd4"
predictionEndpoint = "https://luistrainval.cognitiveservices.azure.com/"
app_name = "luis_train_pred175"
version_id = "0.1"
culture = "en-us"
app_description = "Flight booking App built with LUIS Python SDK."
# raw data path
# data_path = './data/frames/frames.json'
data_path = "data/frames/frames.json"


# Instantiate clients
client, clientRuntime = luis_functions.instantiate_luis_clients(
    authoringEndpoint, authoringKey, predictionEndpoint, predictionKey
)
print("Clients instantiated.")
print()

# Créer une application LUIS
app_id, version_id = luis_functions.create_luis_app(
    client, app_name, version_id, culture, app_description
)
print("App is created.")

# Créer des intents LUIS
luis_functions.add_luis_intents(client, app_id, version_id)
print("Intents have been added to app.")

# Créer des entités LUIS
luis_functions.add_luis_entities(client, app_id, version_id)
print("All entities are added.")

# traiter les données brutes
test_df, train_df, val_df = luis_functions.clean_split_data(data_path)
print("Train shape: ", train_df.shape)
print("Validation shape: ", val_df.shape)
print("Test shape: ", test_df.shape)

# ajouter des exemples d'énoncés à luis
train_utterances = luis_functions.train_utterances(train_df)
with open("data/train_utterances.json", "w+") as f:
    json.dump(train_utterances, f)  # Save the data
print("train_utterance json has been created")

# le json de train_utterenence est analysé pour produire des lots de 100 utterences.
for c in range(0, len(train_utterances), 100):
    d = c + 100
    if d > len(train_utterances):
        d = len(train_utterances)
    luis_functions.add_luis_batch_utterances(
        client, app_id, version_id, train_utterances[c:d]
    )
print("train_utterance json has been added to app.")

# application et publier l'application luis
response_get_endpoint = luis_functions.train_publish_luis_app(
    client, app_id, version_id
)

# créer val utterence json
val_utterance = luis_functions.val_utterances(val_df)
with open("data/val_utterance.json", "w+") as f:
    json.dump(val_utterance, f)  # Save the data
print("val_utterance json has been created.")

# envoyer 1 requête test
text_returned, top_intent, intents, entities = luis_functions.luis_prediction(
    clientRuntime, app_id
)
print("text: ", text_returned)
print("top intent: ", top_intent)
for intent in intents:
    print("More information on intents:", intent.intent, intent.score)
for entity in entities:
    print(
        "More information on entities:",
        entity.type,
        entity.entity,
        entity.additional_properties,
    )

# obtenir des résultats de validation
results_validation = luis_functions.get_results_validation(
    predictionKey, response_get_endpoint, val_utterance
)

# calculer la précision de l'intention
luis_functions.get_validation_intent_accuracy(results_validation, val_df)

# obtenir la précision de l'entité
luis_functions.get_validation_entites_accuracy(results_validation, val_df)
