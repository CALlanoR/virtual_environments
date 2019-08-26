import os

class DatabaseConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = ''mysql://dev:123456@172.21.0.2/MyDBMovies')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config_by_name = dict(
    db=DatabaseConfig
)