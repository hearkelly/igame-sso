# import os

from flask import flash, render_template, redirect, request, url_for, jsonify, session
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from utilities import get_games, get_game_info, game_finder, \
    get_list, get_genres, get_themes, get_similar, get_platforms, get_filters, \
    get_game_names
from . import main
from .forms import GameForm, RatingForm, GameSelections
from ..models import Game, db
from flask_login import login_required, current_user
# from iGame import cache


"""
idea
TODO:
    CREATE custom route decorator to check num of games > 5; if not, send to main.gameForm
    CHANGE how we access user games, currently: session['bag']

views.py NOTES:
    current_user available; full access to User object not needed here
    use global current_user to access user attributes like: id
"""
@main.before_request
def log_request():
    print(f"Request to {request.path}")
    
@main.route('/googleef9fe119bc4df3ad.html')
def google_verify():
    return render_template("googleef9fe119bc4df3ad.html")

@main.route('/add/<gameID>')
@login_required
def add(gameID):
    new = Game(current_user.id, gameID, True)
    try:
        db.session.add(new)
        db.session.commit()
        session['bag'].append(new.to_dict())
        flash('Game added to bag!')
    except SQLAlchemyError as error:
        print(error)
    # session['bag'] = [g.to_dict() for g in
    #                   db.session.query(Game).filter(and_(Game.user_id == current_user.id, Game.likes == True)).all()]
    # session['unbag'] = [g.to_dict() for g in
    #                     db.session.query(Game).filter(and_(Game.user_id == current_user.id, Game.likes == False)).all()]
    return redirect(url_for('main.bag'))


@main.route('/delete/<gameID>')
@login_required
def delete(gameID):
    item = db.session.query(Game).filter(
        and_(Game.user_id == current_user.id, Game.game_id == gameID)).first()
    if item:
        try:
            db.session.delete(item)
            db.session.commit()
            flash('Game removed from bag!')
        except SQLAlchemyError as error:
            print(error)
    else:
        flash('Game not found.')
    session['bag'] = [g.to_dict() for g in
                      db.session.query(Game).filter(and_(Game.user_id == current_user.id, Game.likes == True)).all()]
    return redirect(url_for('main.bag'))

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return redirect((url_for('auth.login')))






@main.route('/home', methods=['GET'])
@login_required
def home():
    """
    NOTES:
    in return, explain why the return of that game
    """
    bag = session['bag']
    unbag = session['unbag']
    if len(bag) + len(unbag) < 5:
        flash("First, we need to know which games you like or not.")
        return redirect(url_for('main.gameForm'))
    bagGames = [g['game_id'] for g in bag]
    unbagGames = [g['game_id'] for g in unbag]
    top5 = get_recs(bagGames, unbagGames)
    top5 = sorted(top5, key=lambda g: g['rating'], reverse=True)
    return render_template('home.html', title="iGame - Dashboard", top5=top5)


@main.route('/gameForm', methods=['GET', 'POST'])
@login_required
# @cache.cached()
def gameForm():
    """
    to collect 5 games: 3 likes, 2 dislikes
    """
    if len(session['bag']) + len(session['unbag']) >= 5:
        return redirect(url_for('main.home'))
    form = GameForm()
    choices = {}
    if form.validate_on_submit():
        query = {'game1': form.game1.data, 'game2': form.game2.data, 'game3': form.game3.data, 'game4': form.game4.data,
                 'game5': form.game5.data}  # get search terms
        for k, v in query.items():
            games = get_games(v)
            if games:
                choices[k] = games
            else:
                flash('No games found for: ' + v)
                return render_template('gameform1.html', form=form, title='iGame - Game Preferences')
        if len(choices) == 5:
            session['options'] = choices
        return redirect(url_for('main.gameForm2'))
    return render_template('gameform1.html', form=form, title='iGame - Game Preferences')


@main.route('/gameForm2', methods=['GET', 'POST'])
@login_required
# @cache.cached()
def gameForm2():
    form = GameSelections()
    games = session.get('options')
    form.game1sel.choices = [(g['id'], g['name'] + "on" + str(g['platforms'])) for g in games.get('game1')]
    form.game2sel.choices = [(g['id'], g['name'] + "on" + str(g['platforms'])) for g in games.get('game2')]
    form.game3sel.choices = [(g['id'], g['name'] + "on" + str(g['platforms'])) for g in games.get('game3')]
    form.game4sel.choices = [(g['id'], g['name'] + "on" + str(g['platforms'])) for g in games.get('game4')]
    form.game5sel.choices = [(g['id'], g['name'] + "on" + str(g['platforms'])) for g in games.get('game5')]
    if form.is_submitted():
        likes = (form.game1sel.data,
                 form.game2sel.data,
                 form.game3sel.data)
        dislikes = (form.game4sel.data,
                    form.game5sel.data)
        for gameID in likes:
            userGame = Game(current_user.id, gameID, True)
            db.session.add(userGame)
        for gameID in dislikes:
            userGame = Game(current_user.id, gameID, False)
            db.session.add(userGame)
        db.session.commit()
        return redirect(url_for('main.home'))
    return render_template('gameform2.html', form=form, title='iGame - Game Preferences')


@main.route('/rate/<gameID>', methods=['GET', 'POST'])
@login_required
def rate(gameID):
    form = RatingForm()
    if form.validate_on_submit():  # NEED TO VERIFY that gameID exists
        rated = db.session.query(Game).filter(
            and_(Game.user_id == current_user.id, Game.game_id == gameID)).first()
        try:
            rated.rating = form.gameRating.data
            db.session.commit()
            flash('Rating saved.')
        except Exception as e:
            flash('Rating not saved.')
    return redirect(url_for('main.bag'))


@main.route('/bag')
@login_required
def bag():
    """
    let's return a list of {} with keys for gameID, gameName, gameRating
    """
    form = RatingForm()
    items = db.session.query(Game.game_id, Game.rating).filter(
        and_(Game.user_id == current_user.id, Game.likes == True)).all()
    if not items:
        return render_template('bag.html', games=[], form=form)
    named = get_game_names(items)
    sortedBag = sorted(named, key=lambda g: str(g['name']))
    return render_template('bag.html', games=sortedBag, form=form)


@main.route('/gameFinder/<id_>')
@login_required
# @cache.cached(timeout=600)
def game(id_):
    """
    :param id_:
    :return:
    """
    # cover, platforms, genres, themes, rating
    platforms, modes, genres, themes, screenshot_url, cover_url = [], [], [], [], [], None
    info_dict = get_game_info(id_)
    name = info_dict.get('name')
    if info_dict.get('platforms'):
        platforms = [platform.get('name') for platform in info_dict.get('platforms')]
    if info_dict.get('cover'):
        cover_url = info_dict.get('cover').get('url')
    if info_dict.get('game_modes'):
        modes = [mode.get('name') for mode in info_dict.get('game_modes')]
    if info_dict.get('genres'):
        genres = [genre.get('name') for genre in info_dict.get('genres')]
    if info_dict.get('themes'):
        themes = [theme.get('name') for theme in info_dict.get('themes')]
    rating = info_dict.get('rating')
    if info_dict.get('screenshots'):
        screenshot_url = [shot.get('url') for shot in info_dict.get('screenshots')]
    story = info_dict.get('storyline')
    sum = info_dict.get('summary')
    infoDict = {'name': name, 'platforms': platforms, 'cover_url': cover_url, 'modes': modes,
                'genres': genres, 'themes': themes, 'rating': rating, 'screenshot_url': screenshot_url, 'story': story,
                'sum': sum}
    return jsonify({'gameInfo': infoDict})


# to do: cache game finder filters
@main.route('/gameFinder', methods=['GET', 'POST'])
@login_required
def gameFinder():
    """
    todoLagain, can option names be generated directly in jinja?
    :return:
    """
    if session.get('theme') is None:
        session['platformCat'], session['platformFam'], session['genre'], session['mode'], session[
            'theme'] = get_filters()
    games = []
    platformCategoriesChoices = [(choice.get('id'), choice.get('name')) for choice in session['platformCat']]
    platformFamilyChoices = [(choice.get('id'), choice.get('name')) for choice in session['platformFam']]
    game_modeChoices = [(choice.get('id'), choice.get('name')) for choice in session['mode']]
    themesChoices = [(choice.get('id'), choice.get('name')) for choice in session['theme']]
    genresChoices = [(choice.get('id'), choice.get('name')) for choice in session['genre']]
    if request.method == 'POST':
        selectPlatformCat = request.form.getlist('platformCat')
        selectPlatformFam = request.form.getlist('platformFam')
        selectThemes = request.form.getlist('theme')
        selectGenres = request.form.getlist('genre')
        selectModes = request.form.getlist('mode')
        selectPlatformCat = [eval(int_) for int_ in selectPlatformCat]
        selectPlatformFam = [eval(int_) for int_ in selectPlatformFam]
        selectThemes = [eval(int_) for int_ in selectThemes]
        selectGenres = [eval(int_) for int_ in selectGenres]
        selectModes = [eval(int_) for int_ in selectModes]
        gameList = game_finder(selectPlatformCat, selectPlatformFam, selectThemes, selectGenres, selectModes)
        games = gameList[:5]
    return render_template('gamefinder.html',
                           platformCategories=platformCategoriesChoices,
                           platformFamilies=platformFamilyChoices,
                           themes=themesChoices,
                           genres=genresChoices,
                           modes=game_modeChoices,
                           games=games)


@main.route('/docs')
def docs():
    return '<h1>Docs/Manual/FAQ</h1>'


@main.route('/user')
@login_required
def user():
    return '<h1>User Details</h1>'


# @cache.memoize(timeout=300)
def get_recs(bagGames, unbagGames):
    hiGenre = get_genres(bagGames)
    noGenre = get_genres(unbagGames)
    hiTheme = get_themes(bagGames)
    noTheme = get_themes(unbagGames)
    hiGenre = hiGenre - noGenre
    loGenre = hiGenre & noGenre
    noGenre = noGenre - hiGenre
    hiTheme = hiTheme - noTheme
    loTheme = hiTheme & noTheme
    noTheme = loTheme - hiTheme
    try:
        # get similar games, remove games already in bag
        similar = list(get_similar(bagGames) - set(bagGames))
    except ValueError:
        flash('There seem to be no games in your bag.')  # this should not happen
        return redirect(url_for('main.gameForm'))

    # get the platforms for all the games the user has played
    allGames = bagGames + unbagGames
    platforms = list(get_platforms(allGames))

    hiRecs, similar = get_list(similar, platforms, hiGenre, noGenre, hiTheme, noTheme)

    if len(similar) >= 1 and len(hiRecs) < 5:
        loRecs, similar = get_list(similar, platforms, loGenre, noGenre, loTheme, noTheme)
        hiRecs += loRecs
    return hiRecs[:5]
