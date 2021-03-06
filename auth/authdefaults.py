
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import g

# rethink imports
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

# rethink configuration
from app.config import rdb


########################################################################################################################
## Helper Functions
########################################################################################################################

def default_users(database):
    """
    A small function to verify RethinkDB Tables
    Runs once on database initialization.
    """
    conn = r.connect(host=rdb['host'], port=rdb['port'])
    try:
        db = rdb[database].split(':')
        r.db(db[0]).table(db[1]).insert([
            {
                "active": True,
                "admin": True,
                "email": "kamilion@gmail.com",
                "identity_yubico":  "ccccccdbildi",
                "password": ""
            }, {
                "active": True,
                "admin": True,
                "email": "kyle@ospnet.org",
                "identity_yubico": "vvddngikvgln",
                "password": ""
            }, {
                "active": True,
                "admin": True,
                "email": "dwfreed@mtu.edu",
                "identity_yubico": "ccccccbcjegt",
                "password": ""
            }
        ]).run(conn)
        print("AUTHMODELDEFAULTS: STARTUP: User Table defaults initialized.")
    except RqlRuntimeError:
        print("AUTHMODELDEFAULTS: STARTUP: User Table already exists, won't reinitialize.")
    finally:
        conn.close()

def index_setup(database, index_name):
    """
    A small function to verify RethinkDB Tables
    Runs once on application startup.
    """
    conn = r.connect(host=rdb['host'], port=rdb['port'])
    try:
        db = rdb[database].split(':')
        r.db(db[0]).table(db[1]).index_create(index_name).run(conn)
        print("AUTHMODELDEFAULTS: STARTUP: User Table initialized.")
    except RqlRuntimeError:
        print("AUTHMODELDEFAULTS: STARTUP: User Table exists.")
    finally:
        conn.close()

def table_setup(database):
    """
    A small function to verify RethinkDB Tables
    Runs once on application startup.
    """
    conn = r.connect(host=rdb['host'], port=rdb['port'])
    try:
        db = rdb[database].split(':')
        r.db(db[0]).table_create(db[1]).run(conn)
        index_setup(database, 'email')
        default_users(database)
        print("AUTHMODELDEFAULTS: STARTUP: User Table initialized.")
    except RqlRuntimeError:
        print("AUTHMODELDEFAULTS: STARTUP: User Table exists.")
    finally:
        conn.close()

def db_setup(database):
    """
    A small function to verify RethinkDB Databases.
    Runs once on application startup.
    """
    conn = r.connect(host=rdb['host'], port=rdb['port'])
    try:
        db = rdb[database].split(':')
        r.db_create(db[0]).run(conn)
        print("AUTHMODELDEFAULTS: STARTUP: User Database initialized.")
    except RqlRuntimeError:
        print("AUTHMODELDEFAULTS: STARTUP: User Database exists.")
    finally:
        conn.close()
        table_setup(database)

