
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
cdb = 'statedb'

# Import regex support
import re

########################################################################################################################
## Helper Functions
########################################################################################################################

# db setup; only runs once
def db_setup():
    conn = r.connect(host=rdb['host'], port=rdb['port'])
    try:
        db = rdb['statedb'].split(':')
        r.db_create(db[0]).run(conn)
        print("MACHINEMODEL: STARTUP: MachineState Database initialized.")
    except RqlRuntimeError:
        print("MACHINEMODEL: STARTUP: MachineState Database exists.")
    finally:
        conn.close()


# table setup; only runs once
def table_setup():
    conn = r.connect(host=rdb['host'], port=rdb['port'])
    try:
        db = rdb['statedb'].split(':')
        r.db(db[0]).table_create(db[1]).run(conn)
        #r.db(db[0]).table(db[1]).index_create('updated_at').run(conn)
        print("MACHINEMODEL: STARTUP: MachineState Table initialized.")
    except RqlRuntimeError:
        print("MACHINEMODEL: STARTUP: MachineState Table exists.")
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
## Machines Class
########################################################################################################################

# This class represents a Machine in RethinkDB.
class Machine():
    id = None
    machine_id = None
    boot_id = None
    ip = None
    updated_at = None
    disks = {}

    def __init__(self, uuid):
        """
        Create an object from a RethinkDB document
        @param uuid: The RethinkDB UUID to request
        """
        try:
            db = rdb['statedb'].split(':')
            results = r.db(db[0]).table(db[1]).get(uuid).run(g.rdb_conn)
        except RqlRuntimeError:
            print("MACHINEMODEL: InitMachine: Critical Failure: Saving Throw Failed! while looking up UUID: {}".format(uuid))

        if results is None:
            raise NoSuchUUIDExists

        self.id = results['id']
        self.machine_id = results['machine_id']
        self.boot_id = results['boot_id']
        self.updated_at = results['updated_at']

        # These fields may potentially be missing.
        try:
            self.ip = results['ip']
        except KeyError:
            self.ip = "0.0.0.0"
        try:
            self.disks = results['disks']
        except KeyError:
            self.disks = {}

        print("MACHINEMODEL: InitMachine: {} Boot_ID: {} Machine_IP: {}".format(
            self.machine_id, self.boot_id, self.ip))


    # Convenience method
    @classmethod
    def create(cls, machine_id, boot_id):
        """
        Create a new machine entry from a machine_id and boot_id
        @param machine_id: The email address to register with RethinkDB
        @param boot_id: The password to register with RethinkDB
        @return: A Machine object instantiated from the requested machine_id, or None.
        """
        try:  # To make the database entry with the machine_id
            db = rdb['statedb'].split(':')
            inserted = r.db(db[0]).table(db[1]).insert(
                {"machine_id": machine_id, "boot_id": boot_id}
            ).run(g.rdb_conn)
        except RqlRuntimeError:
            return None

        return Machine(inserted['generated_keys'][0])


    # Convenience method
    @classmethod
    def get_machineid_from_bootid(cls, boot_id):
        """
        Create a Machine object from a boot_id
        @param boot_id: The boot_id to request from RethinkDB
        @return: A Machine object instantiated from the requested boot_id, or None.
        """
        if boot_id == "None":
            return None
        else:
            try:
                db = rdb['statedb'].split(':')
                cursor = r.db(db[0]).table(db[1]).filter(
                    {'boot_id': boot_id}
                ).pluck('id').run(g.rdb_conn)
                for document in cursor:
                    return Machine(document['id'])
            except RqlRuntimeError:
                return None

    def __repr__(self):
        return '<Machine {} Boot: {} ip: {}>'.format(self.machine_id, self.boot_id, self.ip)
