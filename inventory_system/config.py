import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'mysql://user1:test123@localhost/inventory_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    MONGO_URI='mongodb://localhost:27017/inventory_db'
