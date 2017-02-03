"""Main configuration file"""
import os


class Config(object):
    abspath = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = "PUT_YOUR_SECRET_KEY_HERE"
    SQLALCHEMY_DATABASE_URI = 'sqlite:////%s/../db.sqlite' % abspath
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ..TODO: Make this actually changable - remove ugly tentacles from the codebase
    UPLOADED_PHOTOS_DEST = "YAuB/static/img/"
