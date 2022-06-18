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