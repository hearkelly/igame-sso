from flask import Blueprint

auth = Blueprint('auth', __name__)
print(type(auth))
from . import views
