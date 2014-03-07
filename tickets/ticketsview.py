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
cdb = 'ticketsdb'


########################################################################################################################
## View Class
########################################################################################################################
class TicketsView(FlaskView):
    decorators = [login_required]

    def index(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).run(g.rdb_conn))
        if selection is not None:
            print(selection)
            return render_template('tickets/ticketslist.html', results=selection)
        else:
            return "Not Found", 404

    def get(self, uuid):
        db = rdb[cdb].split(':')
        selection = r.db(db[0]).table(db[1]).get(uuid).run(g.rdb_conn)
        if selection is not None:
            print(selection)
            return render_template('tickets/ticket.html', results=selection)
        else:
            return "Not Found", 404
