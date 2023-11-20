import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine('postgresql://hearkelly:8608!06aeAWS@igame-hk.c2hiop2hj9wf.us-east-2.rds.amazonaws.com/igame')

try:
    connection=engine.connect()
    print("Database connected")

    result = connection.execute('SELECT 1')
    print(result.fetchone())

except Exception as e:
    print(e)

