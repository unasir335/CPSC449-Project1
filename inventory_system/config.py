import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.urandom(24)
    
    #mysql config
    SQLALCHEMY_DATABASE_URI = 'sqlite:///inventory.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    #mongodb config
    MONGO_URI='mongodb://localhost:27017/inventory_db'
