from pprint import pprint
import os
import requests.exceptions
from igdb.wrapper import IGDBWrapper
from more_itertools import collapse
import json
import hashlib

# import from env var or tokens.py
# .get() is currently set in a .env file
WRAPPER = IGDBWrapper('x80ohduafgkshvv7rnsf1r3c8nd5lz', '4us8cgnvbegtoc240fp9uiynrj30v1')

def get_game_info(id_: int):
    # cover, platforms, age rating, mode, genres, themes, rating, summary
    try:
        rq = WRAPPER.api_request(
            'games',
            f'f name, cover.url; where id = {id_};'
        )
        response = json.loads(rq)
        if len(response) == 1:
            return response[0]
    except requests.exceptions.HTTPError as err:
        print(f"{err}")
        return None

print(get_game_info(13000))
