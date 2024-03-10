import pathlib
import os

BASE_DIR = pathlib.Path(__file__).parent


class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://" + os.environ.get("POSTGRES_USER") + ":" + \
                              os.environ.get("POSTGRES_PASSWORD") + "@localhost/" + os.environ.get("POSTGRES_DB_NAME")


    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
