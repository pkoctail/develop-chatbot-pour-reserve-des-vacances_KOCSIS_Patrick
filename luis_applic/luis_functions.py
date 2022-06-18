import pandas as pd
import numpy as np
import time
import json
from sklearn.model_selection import train_test_split
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.language.luis.authoring.models import (
    ApplicationCreateObject,
)
import requests

# Instanciation des clients
def instantiate_luis_clients(
    authoringEndpoint, authoringKey, predictionEndpoint, predictionKey
):
    # Instanciation d'un client de création LUIS
    client = LUISAuthoringClient(
        authoringEndpoint, CognitiveServicesCredentials(authoringKey)
    )
    # Instanciation d'un client d'exécution LUIS
    runtimeCredentials = CognitiveServicesCredentials(predictionKey)
    clientRuntime = LUISRuntimeClient(
        endpoint=predictionEndpoint, credentials=runtimeCredentials
    )

    return client, clientRuntime


# Créer une application LUIS
def create_luis_app(client, app_name, version_id, culture, app_description):
    """Création d'une application LUIS avec un client instancié et les variables mentionnées ci-dessus."""
    # Call the details
    appDefinition = ApplicationCreateObject(
        name=app_name,
        initial_version_id=version_id,
        culture=culture,
        description=app_description,
    )
    app_id = client.apps.add(appDefinition)
    print("Created LUIS app {}\n  with ID {}".format(app_name, app_id))
    return app_id, version_id


# Créer des intents LUIS
def add_luis_intents(client, app_id, version_id):
    """Ajouter des intentions en utilisant la méthode add intent"""
    list_of_intents = ["BookFlight", "Cancel"]
    for intent in list_of_intents:
        intentid = client.model.add_intent(app_id, version_id, intent)
        print("{} ID {} added.".format(intent, intentid))


# Créer des entités LUIS
def add_luis_entities(client, app_id, version_id):
    # ajouter toutes les entités à l'intention de booktravel
    # entité mère
    city_ID = {"name": "city"}

    origin = client.model.add_entity(app_id, version_id, name="or_city")
    print("Entity {} {} added.".format("or_city", origin))

    destination = client.model.add_entity(app_id, version_id, name="dst_city")
    print("Entity {} {} added.".format("dst_city", destination))

    start_date = client.model.add_entity(app_id, version_id, name="str_date")
    print("Entity {} {} added.".format("str_date", start_date))

    end_date = client.model.add_entity(app_id, version_id, name="end_date")
    print("Entity {} {} added.".format("end_date", end_date))

    budget = client.model.add_entity(app_id, version_id, name="budget")
    print("Entity {} {} added.".format("budget", budget))