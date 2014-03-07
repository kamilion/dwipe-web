
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
cdb = 'ticketsdb'

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
        print("TICKETSMODEL: STARTUP: Tickets Database initialized.")
    except RqlRuntimeError:
        print("TICKETSMODEL: STARTUP: Tickets Database exists.")
    finally:
        conn.close()


# table setup; only runs once
def table_setup():
    conn = r.connect(host=rdb['host'], port=rdb['port'])
    try:
        db = rdb[cdb].split(':')
        r.db(db[0]).table_create(db[1]).run(conn)
        #r.db(db[0]).table(db[1]).index_create('updated_at').run(conn)
        print("TICKETSMODEL: STARTUP: Tickets Table initialized.")
    except RqlRuntimeError:
        print("TICKETSMODEL: STARTUP: Tickets Table exists.")
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
## Tickets Class
########################################################################################################################

# This class represents a Ticket in RethinkDB.
class Ticket():
    id = None
    updated_at = None
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
            print("TICKETSMODEL: InitTicket: Critical Failure: Saving Throw Failed! while looking up UUID: {}".format(uuid))

        if results is None:
            raise NoSuchUUIDExists

        self.id = results['id']
        self.updated_at = results['updated_at']


        # These fields may potentially be missing.
        try:
            self.success = results['success']
        except KeyError:
            self.success = False

        try:
            self.ip = results['ip']
        except KeyError:
            self.ip = "0.0.0.0"

        try:
            self.results = results
        except KeyError:
            self.results = {}

        print("TICKETSMODEL: Ticket: {} Boot_ID: {} Machine_IP: {}".format(
            self.machine_id, self.boot_id, self.ip))

    # Convenience method
    @classmethod
    def create(cls, user_id):
        """
        Create a new Ticket entry from a user_id and boot_id
        @param user_id: The User's UUID creat the ticket with RethinkDB
        @return: A Ticket object instantiated from the requested user_id, or None.
        """
        try:  # To make the database entry with the user_id
            db = rdb[cdb].split(':')
            inserted = r.db(db[0]).table(db[1]).insert({
                "user_id": user_id,
                "updated_at": r.now()
            }).run(g.rdb_conn)
        except RqlRuntimeError:
            return None

        return Ticket(inserted['generated_keys'][0])

    def __repr__(self):
        return '<Ticket {} Boot: {}>'.format(self.id, self.boot_id)
