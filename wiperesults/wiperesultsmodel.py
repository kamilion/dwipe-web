
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import g

# Rethink imports
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

# Rethink configuration
from app.config import rdb
# This Class uses database configuration:
cdb = 'wipedb'

# Import regex support
import re

########################################################################################################################
## Helper Functions
########################################################################################################################

# db setup; only runs once
def db_setup():
    conn = r.connect(host=rdb['host'], port=rdb['port'])
    try:
        db = rdb[cdb].split(':')
        r.db_create(db[0]).run(conn)
        print("WIPERESULTSMODEL: STARTUP: MachineState Database initialized.")
    except RqlRuntimeError:
        print("WIPERESULTSMODEL: STARTUP: MachineState Database exists.")
    finally:
        conn.close()


# table setup; only runs once
def table_setup():
    conn = r.connect(host=rdb['host'], port=rdb['port'])
    try:
        db = rdb[cdb].split(':')
        r.db(db[0]).table_create(db[1]).run(conn)
        #r.db(db[0]).table(db[1]).index_create('updated_at').run(conn)
        print("WIPERESULTSMODEL: STARTUP: MachineState Table initialized.")
    except RqlRuntimeError:
        print("WIPERESULTSMODEL: STARTUP: MachineState Table exists.")
    finally:
        conn.close()

# Run these tasks when we're first imported by uwsgi or executed.
db_setup()
table_setup()

########################################################################################################################
## Utility Classes
########################################################################################################################

class NoSuchUUIDExists(Exception):
    pass


########################################################################################################################
## WipeResults Class
########################################################################################################################

# This class represents a WipeResult in RethinkDB.
class WipeResult():
    id = None
    machine_id = None
    boot_id = None
    updated_at = None
    name = None
    model = None
    serial = None
    progress = ""
    progress_bar = ""
    time_elapsed = ""
    time_remaining = ""
    total_megs = 0
    read_megs = 0
    speed_megs = 0
    completed = False
    finished = False
    success = False
    results = {}

    def __init__(self, uuid):
        """
        Create an object from a RethinkDB document
        @param uuid: The RethinkDB UUID to request
        """
        try:
            db = rdb[cdb].split(':')
            results = r.db(db[0]).table(db[1]).get(uuid).run(g.rdb_conn)
        except RqlRuntimeError:
            print("WIPERESULTSMODEL: InitWipeResult: Critical Failure: Saving Throw Failed! while looking up UUID: {}".format(uuid))

        if results is None:
            raise NoSuchUUIDExists

        self.id = results['id']
        self.updated_at = results['updated_at']
        self.name = results['name']
        self.model = results['model']
        self.serial = results['serial']
        self.progress = results['progress']
        self.progress_bar = results['progress_bar']
        self.time_elapsed = results['time_elapsed']
        self.time_remaining = results['time_remaining']
        self.total_megs = results['total_megs']
        self.read_megs = results['read_megs']
        self.speed_megs = results['speed_megs']
        self.completed = results['completed']
        self.finished = results['finished']

        # These fields may potentially be missing.
        try:
            self.success = results['success']
        except KeyError:
            self.success = False
        try:
            self.machine_id = results['machine_id']
        except KeyError:
            self.machine_id = None
        try:
            self.boot_id = results['boot_id']
        except KeyError:
            self.boot_id = None
        try:
            self.ip = results['ip']
        except KeyError:
            self.ip = "0.0.0.0"
        try:
            self.results = results
        except KeyError:
            self.results = {}

        print("WIPERESULTSMODEL: WipeResult: {} Boot_ID: {} Machine_IP: {}".format(
            self.machine_id, self.boot_id, self.ip))

    def __repr__(self):
        return '<WipeResult {} Boot: {}>'.format(self.id, self.boot_id)
