# settings.py
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_HOST = os.environ.get("AWS_HOST")
AWS_REGION = os.environ.get("AWS_REGION")
COUCH_DB_USER = os.environ.get("COUCH_DB_USER")
COUCH_DB_PWD = os.environ.get("COUCH_DB_PWD")
COUCH_DB_URL = os.environ.get("COUCH_DB_URL")
COUCH_DB_ADMIN_USER = os.environ.get("COUCH_DB_ADMIN_USER")
COUCH_DB_ADMIN_PWD = os.environ.get("COUCH_DB_ADMIN_PWD")
ISY_URL = os.environ.get("ISY_URL")
ISY_USER = os.environ.get("ISY_USER")
ISY_PWD = os.environ.get("ISY_PWD")
ISY_TLS_VERSION = os.environ.get("ISY_TLS_VERSION")
PYISY_LOG_LEVEL = os.environ.get("PYISY_LOG_LEVEL")

if ISY_TLS_VERSION not in ["1.1", "1.2"]:
    ISY_TLS_VERSION = 1.2
else:
    ISY_TLS_VERSION = float(ISY_TLS_VERSION)
