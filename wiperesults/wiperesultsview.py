
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify

# Flask-login imports
from flask.ext.login import current_user, login_required

# Flask-classy imports
from flask.ext.classy import FlaskView, route

# rethink imports
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

# rethink configuration
from app.config import rdb
# This Class uses database configuration:
cdb = 'wipedb'

# Pull in our local model
from wiperesultsmodel import WipeResult


########################################################################################################################
## View Class
########################################################################################################################
class WipeResultsView(FlaskView):
    decorators = [login_required]

    def index(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).order_by(
            r.desc('updated_at')
        ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            single = False
            if len(selection) <= 5:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('wipe/results.html', results=selection, single=single)
        else:
            return "Not Found", 404


    def get(self, uuid):
        selection = WipeResult(uuid)
        if selection is not None:
            #print(selection)
            return render_template('wipe/results.html', results={selection}, single=True)
        else:
            return "Not Found", 404

    def get_raw(self, uuid):
        db = rdb[cdb].split(':')
        selection = r.db(db[0]).table(db[1]).get(uuid).run(g.rdb_conn)
        if selection is not None:
            #print(selection)
            return render_template('wipe/results.html', results=selection, single=True)
        else:
            return "Not Found", 404

    def get_json(self, uuid):
        db = rdb[cdb].split(':')
        selection = r.db(db[0]).table(db[1]).get(uuid).run(g.rdb_conn)
        if selection is not None:
            #print(selection)
            return jsonify(selection)
        else:
            return "Not Found", 404

    def find_all(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).order_by(
            r.desc('updated_at')
        ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            single = False
            if len(selection) <= 5:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('wipe/results.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def find_complete(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            {'completed': True}
        ).order_by(
            r.desc('updated_at')
        ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            single = False
            if len(selection) <= 5:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('wipe/results.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def find_success(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            {'success': True}
        ).order_by(
            r.desc('updated_at')
        ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            single = False
            if len(selection) <= 5:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('wipe/results.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def find_running(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            lambda this_machine: this_machine.has_fields('updated_at')
        ).filter(  # Very Yes?
            r.row['updated_at'].during(r.now() - 3600, r.now() + 3600)
        ).order_by(
            r.desc('updated_at')
        ).filter(
            {'completed': False}
        ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            single = False
            if len(selection) <= 5:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('wipe/results.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def find_recent(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            lambda this_machine: this_machine.has_fields('updated_at')
        ).filter(  # Very Yes?
            r.row['updated_at'].during(r.now() - 3600, r.now() + 3600)
        ).order_by(
            r.desc('updated_at')
        #).filter(
        #    {'completed': False}
        ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            single = False
            if len(selection) <= 5:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('wipe/results.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def find_history(self, past=600):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            lambda this_machine: this_machine.has_fields('updated_at')
        ).filter(  # Very Yes?
            r.row['updated_at'].during(r.now() - int(past), r.now() + 600)
        ).order_by(
            r.desc('updated_at')
        #).filter(
        #    {'completed': False}
        ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            single = False
            if len(selection) <= 5:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('wipe/results.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def find_recent_success(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            lambda this_machine: this_machine.has_fields('updated_at')
        ).filter(  # Very Yes?
            r.row['updated_at'].during(r.now() - 3600, r.now() + 3600)
        ).order_by(
            r.desc('updated_at')
        ).filter(
            {'success': True}
        ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            single = False
            if len(selection) <= 5:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('wipe/results.html', results=selection, single=single)
        else:
            return "Not Found", 404
