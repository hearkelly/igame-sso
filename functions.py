
import os
import requests.exceptions
from igdb.wrapper import IGDBWrapper
from more_itertools import collapse
import json
import hashlib
from iGame import cache


# .get() is currently set in a .env file
WRAPPER = IGDBWrapper(os.environ.get('TWITCH_ID'), os.environ.get('IGDB_TOKEN'))


@cache.memoize(timeout=1209600)
def get_games(term: str):
    """
    returns list of games with id, name, platforms
    """
    search = term.strip()
    gameList = []
    try:
        rq = WRAPPER.api_request('games', f'search "{search}"; f name, platforms.name;')
        response = json.loads(rq)
    except requests.exceptions.HTTPError as err:
        print(f'{err}')
        response = None
    if response:
        for each in response:
            platformList = []
            platforms = each.get('platforms')
            if platforms:
                for platform in platforms:
                    platformList.append(platform.get('name'))
            else:
                platformList = ['None']
            listItem = {'id': each.get('id'), 'name': each.get('name'), 'platforms': platformList}
            gameList.append(listItem)
    return gameList


@cache.memoize(timeout=1209600)
def get_game_info(id_: int):
    # cover, platforms, age rating, mode, genres, themes, rating, summary
    try:
        rq = WRAPPER.api_request(
            'games',
            f'f name, cover.url, summary,storyline,screenshots.url,age_ratings.synopsis,game_modes.name,genres.name,platforms.name,rating,themes.name; where id = {id_};'
        )
        response = json.loads(rq)
        if len(response) == 1:
            return response[0]
    except requests.exceptions.HTTPError as err:
        print(f"{err}")
        return None


@cache.memoize(timeout=1209600)
def game_finder(selectPlatformCategory=(), selectPlatformFamily=(), selectThemes=(), selectGenres=(), selectModes=()):
    rqString = 'f name, cover.url, summary,storyline,screenshots.url,age_ratings.synopsis,game_modes.name,genres.name, platforms.category, platforms.platform_family, rating,themes.name; where rating != null'
    if len(selectPlatformCategory) > 1:
        selectPlatformCategory = tuple(selectPlatformCategory)
        rqString += f'& platforms.category = ({selectPlatformCategory})'
    elif len(selectPlatformCategory) == 1:
        selectPlatformCategory = selectPlatformCategory[0]
        rqString += f'& platforms.category = ({selectPlatformCategory})'
    if len(selectPlatformFamily) > 1:
        selectPlatformFamily = tuple(selectPlatformFamily)
        rqString += f'& platforms.platform_family = ({selectPlatformFamily})'
    elif len(selectPlatformFamily) == 1:
        selectPlatformFamily = selectPlatformFamily[0]
        rqString += f'& platforms.platform_family = ({selectPlatformFamily})'
    if len(selectThemes) > 1:
        selectThemes = tuple(selectThemes)
        rqString += f'& themes = ({selectThemes})'
    elif len(selectThemes) == 1:
        selectThemes = selectThemes[0]
        rqString += f'& themes = ({selectThemes})'
    if len(selectGenres) > 1:
        selectGenres = tuple(selectGenres)
        rqString += f'& genres = ({selectGenres})'
    elif len(selectGenres) == 1:
        selectGenres = selectGenres[0]
        rqString += f'& genres = ({selectGenres})'
    if len(selectModes) > 1:
        selectModes = tuple(selectModes)
        rqString += f'& game_modes = ({selectModes})'
    elif len(selectModes) == 1:
        selectModes = selectModes[0]
        rqString += f'& game_modes = ({selectModes})'
    rq = WRAPPER.api_request('games', f'{rqString}; limit 50; sort rating desc;')
    load = json.loads(rq)

    gameList = []
    for each in load:
        infoDict = {'id': each.get('id'), 'name': each.get('name')}
        if each.get('platforms'):
            infoDict['platforms'] = [platform.get('name') for platform in each.get('platforms')]
        if each.get('cover'):
            infoDict['cover_url'] = each.get('cover').get('url')
        if each.get('game_modes'):
            infoDict['modes'] = [mode.get('name') for mode in each.get('game_modes')]
        if each.get('genres'):
            infoDict['genres'] = [genre.get('name') for genre in each.get('genres')]
        if each.get('themes'):
            infoDict['themes'] = [theme.get('name') for theme in each.get('themes')]
        infoDict['rating'] = each.get('rating')
        if each.get('screenshots'):
            infoDict['screenshot_url'] = [shot.get('url') for shot in each.get('screenshots')]
        infoDict['story'] = each.get('storyline')
        infoDict['sum'] = each.get('summary')
        gameList.append(infoDict)
    return gameList


def hash_pass(password: str):
    """
    :param: password input validated in form
    :return: salted, hashed pass as string
    """
    hashPass = password
    salt = os.environ.get('SALT')
    hashPass += salt
    hashed = hashlib.md5(hashPass.encode())
    return hashed.hexdigest()


def get_game_names(games):
    ids_ = [o[0] for o in games]
    if len(ids_) > 1:
        ids_ = tuple(ids_)
    elif len(ids_) == 1:
        ids_ = ids_[0]
    else:
        return None
    rq = WRAPPER.api_request('games', f'f name; where id = {ids_}; limit {len(ids_)};)')
    resp = json.loads(rq)
    names = {each['id']: each['name'] for each in resp}
    namedGames = []
    for id_, rating in games:
        name = names.get(id_)
        namedGames.append({'id': id_, 'name': name, 'rating': rating})
    return namedGames


@cache.memoize(timeout=1209600)
def get_list(games, plats, hiGen, noGen, hiThm, noThm):
    rqString = 'f name, cover.url, summary,storyline,screenshots.url,age_ratings.synopsis,game_modes.name,genres.name, platforms.name,rating,themes.name;'
    if len(games) > 1:
        games = tuple(games)
    elif len(games) == 1:
        games = games[0]
    rqString += f'where id = {games} '
    if len(plats) > 1:
        plats = tuple(plats)
    elif len(plats) == 1:
        plats = plats[0]
    rqString += f'& platforms.id = ({plats})'
    if len(hiThm) > 1:
        hiThm = tuple(hiThm)
    elif len(hiThm) == 1:
        (hiThm,) = hiThm
    rqString += f'& themes.id = ({hiThm})'
    if len(noThm) > 1:
        noThm = tuple(noThm)
    elif len(noThm) == 1:
        noThm = noThm[0]
    else:
        noThm = 0
    rqString += f'& themes.id != ({noThm})'
    if len(hiGen) > 1:
        hiGen = tuple(hiGen)
    elif len(hiGen) == 1:
        hiGen = hiGen[0]
    rqString += f'& genres.id = ({hiGen})'
    if len(noGen) > 1:
        noGen = tuple(noGen)
    elif len(noGen) == 1:
        noGen = noGen[0]
    rqString += f'& genres.id != ({noGen})'
    print(rqString)
    rq = WRAPPER.api_request('games', f'{rqString} & rating != null; sort rating desc;')
    load = json.loads(rq)

    similar = list(games)
    gameList = []
    for each in load:
        infoDict = {'id': each.get('id'), 'name': each.get('name')}
        if each.get('platforms'):
            infoDict['platforms'] = [platform.get('name') for platform in each.get('platforms')]
        infoDict['cover_url'] = each.get('cover').get('url')
        if each.get('game_modes'):
            infoDict['modes'] = [mode.get('name') for mode in each.get('game_modes')]
        if each.get('genres'):
            infoDict['genres'] = [genre.get('name') for genre in each.get('genres')]
        if each.get('themes'):
            infoDict['themes'] = [theme.get('name') for theme in each.get('themes')]
        infoDict['rating'] = each.get('rating')
        if each.get('screenshots'):
            infoDict['screenshot_url'] = [shot.get('url') for shot in each.get('screenshots')]
        infoDict['story'] = each.get('storyline')
        infoDict['sum'] = each.get('summary')
        similar.remove(infoDict['id'])  # remove recommended game from similar games
        gameList.append(infoDict)  # append gameInfo dictionary to recommendation list
    return gameList, tuple(similar)


@cache.memoize(timeout=1209600)
def get_genres(games: list):
    if len(games) > 1:
        games = tuple(games)
    elif len(games) == 1:
        games = games[0]
    rqString = f'f genres; where id = {games}'
    rq = WRAPPER.api_request('games', f'{rqString};')
    response = json.loads(rq)
    if response:
        genres = set(collapse([each.get('genres') for each in response if each.get('genres')]))
        return genres
    else:
        return None


@cache.memoize(timeout=1209600)
def get_themes(games: list):
    if len(games) > 1:
        games = tuple(games)
    elif len(games) == 1:
        games = games[0]
    rqString = f'f themes; where id = {games}'
    rq = WRAPPER.api_request('games', f'{rqString};')
    response = json.loads(rq)
    if response:
        themes = set(collapse([each.get('themes') for each in response if each.get('themes')]))
        return themes
    else:
        return None


@cache.memoize(timeout=1209600)
def get_similar(games: list):
    if len(games) > 1:
        games = tuple(games)
    elif len(games) == 1:
        games = games[0]
    else:
        raise ValueError('No games provided.')
    rqString = f'f similar_games; where id = {games}'
    rq = WRAPPER.api_request('games', f'{rqString};')
    response = json.loads(rq)
    if response:
        similar = set(collapse([each.get('similar_games') for each in response if each.get('similar_games')]))
        return similar
    else:
        return None


@cache.memoize(timeout=1209600)
def get_platforms(games: list):
    if len(games) > 1:
        games = tuple(games)
    elif len(games) == 1:
        games = games[0]
    rqString = f'f platforms; where id = {games}'
    rq = WRAPPER.api_request('games', f'{rqString};')
    response = json.loads(rq)
    if response:
        platforms = set(collapse([each.get('platforms') for each in response if each.get('platforms')]))
        return platforms
    else:
        return None


@cache.memoize(timeout=1209600)
def get_filters():
    # platforms = []
    # rq = WRAPPER.api_request('platforms', 'f name; limit 500; sort id asc;')
    # response = json.loads(rq)
    # if response:
    #     platforms = response

    platformCategories = [{'id': 1, 'name': 'console'}, {'id': 2, 'name': 'arcade'}, {'id': 3, 'name': 'platform'},
                          {'id': 4, 'name': 'operating system'}, {'id': 5, 'name': 'portable console'},
                          {'id': 6, 'name': 'computer'}]

    platformFamilies = [{'id': 1, 'name': 'Playstation'}, {'id': 2, 'name': 'Xbox'}, {'id': 3, 'name': 'Sega'},
                        {'id': 4, 'name': 'Linux'}, {'id': 5, 'name': 'Nintendo'}]

    modes = []
    rq = WRAPPER.api_request('game_modes', 'f name; limit 500; sort id asc;')
    response = json.loads(rq)
    if response:
        modes = response
    genres = []
    rq = WRAPPER.api_request('genres', 'f name; limit 500; sort name asc;')
    response = json.loads(rq)
    if response:
        genres = response
    themes = []
    rq = WRAPPER.api_request('themes', 'f name; limit 500; sort name asc;')
    response = json.loads(rq)
    if response:
        themes = response
    return platformCategories, platformFamilies, genres, modes, themes
