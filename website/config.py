# -*- encoding: utf-8 -*-
"""
"""
import os
from decouple import config
from yaml import load, dump, safe_load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


CONFIG_FILE = './config/config.yaml'

class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(CONFIG_FILE, 'rt', encoding='utf8') as yml:
        __yaml = safe_load(yml)
    # Set up the App SECRET_KEY    
    SECRET_KEY = __yaml['SECRET_KEY']
    SECURITY_PASSWORD_SALT = __yaml['SECURITY_PASSWORD_SALT']

    BIND_HOST = '0.0.0.0'
    BIND_PORT = '80'

    PROXIED = False
    try:
        PROXIED = __yaml['PROXIED']
    except:
        pass

    SERVER_NAME = None
    try:
        SERVER_NAME = __yaml['SERVER_NAME']
    except:
        pass

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_TRACKABLE = True
    SQLALCHEMY_DATABASE_URI = __yaml['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_BINDS = __yaml['SQLALCHEMY_BINDS']


    # OAuth
    OAUTH_AZURE_APP = __yaml['OAUTH_AZURE_APP']
    OAUTH_AZURE_KEY = __yaml['OAUTH_AZURE_KEY']
    OAUTH_AZURE_AUTH_URL = __yaml['OAUTH_AZURE_AUTH_URL']
    OAUTH_AZURE_TOKEN_URL = __yaml['OAUTH_AZURE_TOKEN_URL']
    OAUTH_AZURE_BASE_URL = __yaml['OAUTH_AZURE_BASE_URL']
    OAUTH_AZURE_SCOPE = __yaml['OAUTH_AZURE_SCOPE']

    # Strategy execution status enpoints
    STATUS_ENDPOINTS = __yaml['STATUS_ENDPOINTS']    
    BABEL_DEFAULT_LOCALE: "en"
    try:
        BABEL_DEFAULT_LOCALE: __yaml['BABEL_DEFAULT_LOCALE']
    except:
        pass
    BABEL_DEFAULT_TIMEZONE: "Asia/Seoul"
    try:
        BABEL_DEFAULT_TIMEZONE = __yaml['BABEL_DEFAULT_TIMEZONE']
    except:
        pass
    
class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY  = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
    DEBUG = True
    
    with open(CONFIG_FILE, 'rt', encoding='utf8') as yml:
        __yaml = safe_load(yml)
    try:
        BIND_HOST = __yaml['BIND_HOST']
    except:
        pass
    try:
        BIND_PORT = __yaml['BIND_PORT']
    except:
        pass


with open(CONFIG_FILE, 'rt', encoding='utf8') as yml:
    __yaml = safe_load(yml)
DEBUG = True
try:
    DEBUG = __yaml['DEBUG']
except:
    pass

try:    
    # Load the configuration using the default values 
    c = DebugConfig() if DEBUG else ProductionConfig()
except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')