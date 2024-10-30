import os
from datetime import timedelta


class Config:
    
    #random key generator
    SECRET_KEY = os.urandom(24)
    
    #ensures cookies are only sent over HTTP
    SESSION_COOKIE_SECURE = True
    
    #prevents javascript from accessing cookies, prevent cross-site scripting (injection of malicious scripts)
    SESSION_COOKIE_HTTPONLY = True
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///inventory.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
