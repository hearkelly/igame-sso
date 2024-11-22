
import json
import os
import requests

"""
IGDB API calls authorize requests using tokens generated from twitch oauth.
updates.py:
    - runs each hour
    - collects associated environment vars 
    - validates token in GET twitch request
    - if not valid, creates new token in POST twitch request
    - if not valid, updates token env var with newly generated token
"""

HEROKU_TOKEN = os.environ.get('HRKU_TOKEN')  # does not expire
TWITCH_ID = os.environ.get('TWITCH_ID')
TWITCH_SECRET = os.environ.get('TWITCH_SECRET')  # twitch credentials to generate igdb_token (our api)
IGDB_TOKEN = os.environ.get('IGDB_TOKEN')
APP_NAME = 'i-game-container1'

def generate_token():  # returns token
    # Endpoint for OAuth token generation
    uri = 'https://id.twitch.tv/oauth2/token'

    # Payload for the POST request
    body = {
        'client_id': TWITCH_ID or '',
        'client_secret': TWITCH_SECRET or '',
        'grant_type': 'client_credentials'
    }

    # Make the POST request
    try:
        rq = requests.post(uri, data=body)
        if rq.status_code == 200:
            response = rq.json()
            print(response)
            new_token = response.get('access_token', None)  # get new token here
    except requests.exceptions.RequestException as e:
        print("Failed to parse JSON, connection error, timeout:", e)
        print("Response text:", rq.text)
    if new_token and validate(new_token):
        return new_token
    else:
        print('No new token.')
        return None


def validate(token):
    print(token)
    uri = 'https://id.twitch.tv/oauth2/validate'
    headers = {
        'Authorization': f'Bearer {token}'
    }

    try:    
        rq = requests.get(uri, headers=headers)
    except requests.exceptions.RequestException as e:
        # if no connection, timeout, http error ...
        print(f'{e}')
        return False
    
    if rq.status_code == 200:
        return True
    else:
        print(f'Invalid. Request status code: {rq.status_code}')
        return False


def update_token(): # api call to heroku, return true
    new_token = generate_token()
    if new_token:
        """
        api call
        """
        uri = f'https://api.heroku.com/apps/{APP_NAME}/config-vars'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.heroku+json; version=3',
            'Authorization': f'Bearer {HEROKU_TOKEN}' or ''
        }
        body = {
            'IGDB_TOKEN':f'{new_token}'
        }
        try:
            rq = requests.patch(uri,headers=headers,json=body)
            if rq.status_code == 200:
                print("Configuration updated!")
                return True
        except requests.exceptions.RequestException as e:
            # if no connection, timeout, http error ...
            print(f'{e}')
            return False
    print("Failed to generate new token.")
    return False
        


token:bool = None
while token is None or not token:
    token = validate(IGDB_TOKEN)
    if not token:
        token = update_token()
    if token:
        print("Token is valid.")


""" GET os.environs for client_id, access token.
    VALIDATE with twitch GET request:
    if valid, do not update heroku config vars
    IF NOT VALID:
        - run POST to twitch, validate, then replace heroku config vars

Keyword arguments:
argument -- description
Return: return_description
"""

