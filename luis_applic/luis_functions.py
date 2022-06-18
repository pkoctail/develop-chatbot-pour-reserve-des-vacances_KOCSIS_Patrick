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

# traiter les données brutes
def clean_split_data(data_path):
    """Le chemin des données brutes est la fonction arg. Cette fonction importe le fichier JSON de Frames:
    a) nettoie les données, b) extrait la première interaction de l'utilisateur.
    c) crée df sur les 5 éléments attendus pour les entités. d) forme/teste la division.
    """
    raw_data = pd.read_json(data_path)
    raw_data[["userSurveyRating", "wizardSurveyTaskSuccessful"]] = [
        [j["userSurveyRating"], j["wizardSurveyTaskSuccessful"]]
        for j in raw_data.labels
    ]
    raw_data.drop("labels", axis=1, inplace=True)
    raw_data.dropna(axis=0, how="any", inplace=True)
    # inclure uniquement les interactions les mieux notées par les utilisateurs pour la formation de luis
    cleaned_data = raw_data[raw_data["userSurveyRating"] >= 4]
    cleaned_data.reset_index(drop=True, inplace=True)
    # Create an empty list to save the result
    list_for_df = []
    # iter à travers la ligne des tours de colonne
    for turn in cleaned_data["turns"]:
        # Create an empty dictionary
        diction_for_list = {}
        # mettre le texte de l'utilisateur dans le dictionnaire
        diction_for_list.update({"text": turn[0].get("text")})
        # accéder aux labels>acts pour pouvoir toucher les args nichés
        for segment in turn[0].get("labels").get("acts"):
            # boucle sur les arguments dans arg
            for argument in segment.get("args"):
                # mettre les paires clé:val dans le dictionnaire
                diction_for_list.update({argument.get("key"): argument.get("val")})
        list_for_df.append(diction_for_list)
    # créer df
    columns = [
        "text",
        "intent",
        "or_city",
        "dst_city",
        "str_date",
        "end_date",
        "budget",
    ]
    df = pd.DataFrame(list_for_df, columns=columns)
    df["intent"] = "BookFlight"
    df["text"] = df["text"].str.lower()
    df = df.replace("-1", np.NaN)
    df = df.drop_duplicates()
    cancel_list = [
        "cancel",
        "exit",
        "exit this session",
        "stop",
        "cancel this session",
        "exit this session",
        "cancel my plans",
        "cancel reservation",
        "cancel booking",
        "call off reservation",
        "scrap plans",
        "scrap reservations",
        "call off reservation",
        "call off booking",
        "withdraw booking",
        "withdraw reservation",
        "discontinue",
        "suspend",
        "suspend my plans",
        "discontinue reservation",
    ]
    df_cancel = pd.DataFrame(cancel_list, columns=["text"])
    df_cancel["intent"] = "Cancel"
    none_list = [
        "Can you book a hotel?",
        "Book me a hotel",
        "Book me a hotel in Toronto",
        "Book me a hotel tomorrow night",
        "Book me a hotel next week",
        "Can you book a restaurant?",
        "Book a restaurant",
        "Book me a restaurant",
        "Book my favorite restaurant in London",
        "I would like to book a hotel in New York",
        "reserve a hotel",
        "reserve for dinner",
        "reserve us a hotel in Paris on september 20 2023",
        "reserve us a hotel in Rome on november 20 2023",
        "book us a hotel in Budapest on november 30 2023",
        "do you like hotels?",
        "how about dinner",
        "just want to type",
        "how about batman movie",
        "going to movies",
        "returning from a game",
        "we are going to a baseball game then coming back for dinner",
    ]
    df_none = pd.DataFrame(none_list, columns=["text"])
    df_none["intent"] = "None"
    final_df = pd.concat([df, df_cancel, df_none], axis=0)
    final_df.reset_index(drop=True, inplace=True)
    print("DataFrame shape", final_df.shape)
    train_val_df, test_df = train_test_split(final_df, test_size=24, random_state=42)
    train_df, val_df = train_test_split(train_val_df, test_size=200, random_state=42)
    train_df.to_csv("data/train_df.csv", index=None)
    val_df.to_csv("data/val_df.csv", index=None)
    test_df.to_csv("data/test_df.csv", index=None)
    return test_df, train_df, val_df


# crée le format luis
def dictionary_luis_utterance(intent, utterance, *labels):
    """Cette fonction formate les données à entraîner sur luis.
    Elle retourne un dictionnaire du texte, de l'intention et un dictionnaire imbriqué de chaque entité,
    et avec sa position de début et de fin dans le texte de l'entité.
    """
    text = utterance.lower()
    # crée un dictionnaire imbriqué pour chaque entité.
    def ent_label(name, val):
        val = val.lower()
        mark = text.index(val)
        return dict(entityName=name, startCharIndex=mark, endCharIndex=mark + len(val))

    return dict(
        text=text,
        intentName=intent,
        entityLabels=[ent_label(a, b) for (a, b) in labels],
    )


# crée le format luis
def train_utterances(train_df):
    """Cette fonction prend un df en entrée, boucle sur les lignes,
    sélectionne les informations dont elle a besoin,
    utilise la fonction dictionary_luis_utterance pour créer le
    fichier json d'entraînement dont elle a besoin.
    """

    utterances_list = []
    # pour exclure les entités ayant des valeurs nan de la liste
    nulls_list = ["nan", "NaN", "", np.nan, None]

    # boucler les lignes dans df
    for index, row in train_df.iterrows():
        # liste pour les entités
        entities = []
        if row.or_city not in nulls_list:
            entities.append(("or_city", row.or_city))
        if row.dst_city not in nulls_list:
            entities.append(("dst_city", row.dst_city))
        if row.str_date not in nulls_list:
            entities.append(("str_date", row.str_date))
        if row.end_date not in nulls_list:
            entities.append(("end_date", row.end_date))
        if row.budget not in nulls_list:
            entities.append(("budget", row.budget))
        # appeler la fonction pour mettre les données dans le format de données LUIS
        dictionary_luis = dictionary_luis_utterance(row[1], row[0], *entities)
        # ajouter la liste avec les dictionnaires
        utterances_list.append(dictionary_luis)

    # mettre les données au format json
    prep_json = json.dumps(utterances_list)
    train_data_for_luis = json.loads(prep_json)

    return train_data_for_luis


# ajouter des exemples d'énoncés à luis
def add_luis_batch_utterances(client, app_id, version_id, train_data_for_luis):
    # les énoncés seront traités par lots
    client.examples.batch(app_id, version_id, train_data_for_luis)


# former et publier luis
def train_publish_luis_app(client, app_id, version_id):
    client.train.train_version(app_id, version_id)
    waiting = True
    while waiting:
        info = client.train.get_status(app_id, version_id)
        # get_status retourne une liste de statuts de formation, un pour chaque modèle.
        # Bouclez à travers eux et assurez-vous que tous sont terminés.
        waiting = any(
            map(
                lambda x: "Queued" == x.details.status
                or "InProgress" == x.details.status,
                info,
            )
        )

        if waiting:
            print("Waiting 40 seconds for training to complete.")
            time.sleep(40)
        else:
            waiting = False
    print("App has been trained.")
    client.apps.update_settings(app_id, is_public=True)
    res_endpoint = client.apps.publish(app_id, version_id, is_staging=False)
    response_get_endpoint = res_endpoint.endpoint_url
    print("App has been published- endpoint:", res_endpoint.endpoint_url)
    return response_get_endpoint


# créer le format luis de validation
def dictionary_luis_val_utterance(intent, utterance, *labels):
    """Cette fonction formate les données à entraîner sur luis.
    Elle retourne un dictionnaire du texte, de l'intention et un dictionnaire imbriqué de chaque entité,
    et avec sa position de début et de fin dans le texte de l'entité.
    """
    text = utterance.lower()
    # crée un dictionnaire imbriqué pour chaque entité.
    def ent_label(name, val):
        val = val.lower()
        mark = text.index(val)
        return dict(entity=name, startPos=mark, endPos=mark + len(val) - 1)

    return dict(
        text=text, intent=intent, entities=[ent_label(a, b) for (a, b) in labels]
    )


# créer le format luis de validation
def val_utterances(val_df):
    """Cette fonction prend un df en entrée, boucle sur les lignes,
    sélectionne les informations dont elle a besoin,
    utilise la fonction dictionary_luis_utterance pour créer le
    fichier json validation dont elle a besoin.
    """

    utterances_list = []
    # pour exclure les entités ayant des valeurs nan de la liste
    nan_list = ["nan", "NaN", "", np.nan, None]

    # boucler les lignes dans df
    for index, row in val_df.iterrows():
        # liste pour les entités
        entities = []
        if row.or_city not in nan_list:
            entities.append(("or_city", row.or_city))
        if row.dst_city not in nan_list:
            entities.append(("dst_city", row.dst_city))
        if row.str_date not in nan_list:
            entities.append(("str_date", row.str_date))
        if row.end_date not in nan_list:
            entities.append(("end_date", row.end_date))
        if row.budget not in nan_list:
            entities.append(("budget", row.budget))
        # appeler la fonction pour mettre les données dans le format de données LUIS
        dictionary_luis = dictionary_luis_val_utterance(row[1], row[0], *entities)
        # ajouter la liste avec les dictionnaires
        utterances_list.append(dictionary_luis)

    # mettre les données au format json
    prep_json = json.dumps(utterances_list)
    val_data_for_luis = json.loads(prep_json)

    return val_data_for_luis

