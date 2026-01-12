import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, URL
from sqlalchemy.exc import OperationalError

from os import getenv
from dotenv import load_dotenv

load_dotenv()

def postgresConnectionString():
    return URL.create(
        "postgresql+psycopg2",
        username=getenv('POSTGRES_USERNAME'),
        password=getenv('POSTGRES_PASSWORD'),
        database=getenv('POSTGRES_DATABASE'),
        host=getenv('POSTGRES_HOST'),
        port=getenv('POSTGRES_PORT')
    )

def postgresConnection():
    connectionString = postgresConnectionString()

    try:
        engine = create_engine(connectionString)
        sessionmaker(bind=engine)
        logging.info('Database connection established.')
        return engine

    except OperationalError as e:
        logging.error(f'Failed connecting to the database: ERROR {e}')

def postgresSession(engine):
    Session = sessionmaker(bind=engine)
    return Session()
