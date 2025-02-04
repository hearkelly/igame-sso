from sqlalchemy import and_, func, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from iGame.models import db, Game, User

MESSAGES = {

}


def add_game(user_id: int, game_id: int) -> tuple:
    try:
        go = Game(user_id, game_id, True)
        db.session.add(go)
        db.session.commit()
        return True, "Game added to bag!"
    except IntegrityError as error:
        print(error)
        return False, "Girl, this game is in your bag!"
    except SQLAlchemyError as error:
        print(error)
        # how detailed do we want error messages? ie, duplicate,primary-key error
        # do we need / want a function to validate game id in db ?
        # in theory, only submitted integers are from javascript .fetch()
        return False, f"Database error: Game not added to your bag!"
    except Exception as error:
        print(error)
        return False, "Application error: Game not added to your bag!"


def delete_game(user_id: int, game_id: int) -> tuple:
    go = db.session.query(Game).filter(
        and_(Game.user_id == user_id, Game.game_id == game_id)).first()
    if go:
        try:
            db.session.delete(go)
            db.session.commit()
            return True, "Game deleted from bag!"
        except SQLAlchemyError as error:
            print(error)
            return False, "Some database error! Game not deleted."
    return False, "Game not found in your bag."


def count_likes(user_id: int) -> int:
    try:
        result = db.session.execute(
            db.select(func.count(Game.game_id)).where(Game.user_id == user_id).where(Game.likes == True)).scalar()
        if isinstance(result,int):
            return result
    except SQLAlchemyError as error:
        print(error)
        return -1
    except Exception as error:
        print(error)
        return -1
    return -1
