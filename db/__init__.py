import contextlib
from cloudant import couchdb
import settings
from models import AwsTellMeTable


def couchdb_admin_session():
    return couchdb(settings.COUCH_DB_ADMIN_USER, settings.COUCH_DB_ADMIN_PWD, url=settings.COUCH_DB_URL)


@contextlib.contextmanager
def get_local_db():
    with couchdb(settings.COUCH_DB_USER, settings.COUCH_DB_PWD, url=settings.COUCH_DB_URL) as session:
        db = session["tellme"]
        yield db


def get_aws_table():
    return AwsTellMeTable
