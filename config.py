#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Configuration for the bot."""
    
    
    #added appID and pass of travelbotproject
    PORT = 8000
    #PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "0aceee94-0d4f-4a1c-a408-58a927d85212")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "ZVt8Q~St4QVJ8_0PFOY2ThGEl-jzTHq3N_eGya3p")
    LUIS_APP_ID = os.environ.get("LuisAppId", "9551a6aa-e958-4e58-8d10-2abe1eb4b4de")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "1f40e3ea26524ae5b2d3fae9da451fd4")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westeurope.api.cognitive.microsoft.com")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "777a0a9c-1230-4c80-90fc-a227aeda2281"
    )