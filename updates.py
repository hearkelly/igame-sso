import os
import requests

"""
note : EXPLICITLY CLOSE DB CONNECTIONS IF USING SQLALCHEMY OUTSIDE OF A FLASK APP CONTEXT

IGDB API calls authorize requests using tokens generated from twitch oauth.
updates.py:
    - runs each hour
    - collects associated environment vars 
    - validates token in GET twitch request
    - if not valid, creates new token in POST twitch request
    - if not valid, updates token env var with newly generated token
"""

APP_NAME = 'i-game-container1'


def generate_token():  # returns token
    new_token = ''
    # Endpoint for OAuth token generation
    uri = 'https://id.twitch.tv/oauth2/token'

    # Payload for the POST request
    body = {
        'client_id': os.environ.get('TWITCH_ID') or '',
        'client_secret': os.environ.get('TWITCH_SECRET') or '',
        'grant_type': 'client_credentials'
    }

    try:
        rq = requests.post(url=uri, json=body)
        rq.raise_for_status()
        response = rq.json()
        new_token = response.get('access_token')
    except requests.exceptions.RequestException as e:
        print("Failed to parse JSON, connection error, timeout:", e)
    if new_token and validate(new_token):
        return new_token
    else:
        print("ERROR.")
        return ''


def validate(_token):
    uri = 'https://id.twitch.tv/oauth2/validate'
    headers = {
        'Authorization': f'Bearer {_token}'
    }
    try:
        rq = requests.get(url=uri, headers=headers)
        rq.raise_for_status()  # replaces checking if request status == 200
        response = rq.json()
        if response['expires_in'] < 60 * 60:  # 'expires_in' value in seconds: int
            return False
        else:
            return True
    except requests.exceptions.RequestException as e:
        # if no connection, timeout, http error ...
        print(f'{e}')
    return False


def update_token():  # api call to heroku, return true
    new_token = generate_token()
    if new_token:  # will not continue if empty string
        """
        api call
        """
        uri = f'https://api.heroku.com/apps/{APP_NAME}/config-vars'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.heroku+json; version=3',
            'Authorization': f"Bearer {os.environ.get('HRKU_TOKEN')}" or ''
        }
        body = {
            'IGDB_TOKEN': new_token
        }
        try:
            rq = requests.patch(uri, headers=headers, json=body)
            rq.raise_for_status()
            print("Configuration updated!")
            return True
        except requests.exceptions.RequestException as e:
            # if no connection, timeout, http error ...
            print(f'{e}')
    return False


def get_current_token():
    """
    access config vars from heroku api
    """
    uri = f'https://api.heroku.com/apps/{APP_NAME}/config-vars'
    headers = {
        'Authorization': f"Bearer {os.environ.get('HRKU_TOKEN')}" or '',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    try:
        rq = requests.get(url=uri, headers=headers)
        rq.raise_for_status()
        response = rq.json()
        return response.get('IGDB_TOKEN')  # TODO: CHANGE CODE VAR NAMES TO MATCH CONFIG
    except requests.exceptions.RequestException as e:
        # if no connection, timeout, http error ...
        # LOG ERROR, return None
        print(e)
        return ''  # I'm returning an empty string to align with JSON format


token: bool = False
while not token:
    current = get_current_token()
    token = validate(current)
    if not token:
        token = update_token()
    print(f"Token Status: {token}")
