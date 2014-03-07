
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# System imports
from time import sleep

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
cdb = 'statedb'

# Pull in our local model
from machinesmodel import Machine

# Temp:
# Redis-Queue imports
import redis
from rq import Queue, Worker, job


########################################################################################################################
## View Class
########################################################################################################################
class MachinesView(FlaskView):
    decorators = [login_required]

    #def index():
    #        form = AuthForm()
    #        if form.validate_on_submit():
    #                r.table('users').insert({"name":form.label.data}).run(g.rdb_conn)
    #                return redirect(url_for('index'))
    #        selection = list(r.table('users').run(g.rdb_conn))
    #        return render_template('index.html', form = form, tasks = selection)



    def index(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            lambda this_user: this_user.has_fields('ip')
        ).filter(
            lambda this_user: this_user.has_fields('updated_at')
        #).filter(  # Old ISO8601-in-string format
        #    lambda row:row['updated_at'].match("^2014")
        #).filter(  # Rethink is unhappy with some lambda expressions
        #    lambda updated_at:
        #    updated_at.during(r.now() - 604800, r.now())
        #).filter(  # This works, but it's ugly
        #    r.row['updated_at'].during(r.time(2014, 1, 1, 'Z'), r.now())
        ).filter(  # Very Yes?
            r.row['updated_at'].during(r.now() - 300, r.now() + 300)
        ).run(g.rdb_conn))
        if selection is not None:
            print(selection)
            print("Length is: ", len(selection), " so expanding items.")
            single = False
            if len(selection) <= 10:
                single = True
            #ticking = r.expr({'now': r.now(), 'ten_ago': r.now() - 300, 'future': r.now() + 300}).run(g.rdb_conn)
            return render_template('machines/machineslist.html', results=selection, single=single) #, thetimeis=ticking)
        else:
            return "Not Found", 404

    def get(self, uuid):
        machine = Machine(uuid)
        if machine is not None:
            print(machine)
            return render_template('machines/machine.html', results={machine})
        else:
            return "Not Found", 404


    def get_json(self, uuid):
        db = rdb[cdb].split(':')
        machine = r.db(db[0]).table(db[1]).get(uuid).run(g.rdb_conn)
        if machine is not None:
            print(machine)
            return jsonify(machine)
        else:
            return "Not Found", 404

    def get_all(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).run(g.rdb_conn))
        if selection is not None:
            print(selection)
            single = False
            if len(selection) <= 10:
                print("Length is: ", len(selection), " so expanding items.")
                single = True

            return render_template('machines/machineslist.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def find_history(self, past=600):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            lambda this_user: this_user.has_fields('ip')
        ).filter(
            lambda this_user: this_user.has_fields('updated_at')
        ).filter(
            r.row['updated_at'].during(r.now() - int(past), r.now() + 3600)
        ).order_by(
            r.desc('updated_at')
        ).run(g.rdb_conn))
        if selection is not None:
            print(selection)
            single = False
            if len(selection) <= 10:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('machines/machineslist.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def today(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            lambda this_user: this_user.has_fields('ip')
        ).filter(
            lambda this_user: this_user.has_fields('updated_at')
        ).filter(
            r.row['updated_at'].during(r.now() - 86400, r.now() + 3600)
        ).run(g.rdb_conn))
        if selection is not None:
            print(selection)
            single = False
            if len(selection) <= 10:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('machines/machineslist.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def this_week(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            lambda this_user: this_user.has_fields('ip')
        ).filter(
            lambda this_user: this_user.has_fields('updated_at')
        ).filter(
            r.row['updated_at'].during(r.now() - 604800, r.now() + 3600)
        ).run(g.rdb_conn))
        if selection is not None:
            print(selection)
            single = False
            if len(selection) <= 10:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('machines/machineslist.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def start_wipe(self, uuid, device):
        machine = Machine(uuid)
        if machine is not None:
            print("Attempting to start wipe, machine:")
            print(machine)
            print("Attempting to connect to redis on {}".format(machine.ip))
            target_device = "/dev/{}".format(device)

            # Redis queue connection setup so we can pass authentication
            q = Queue(connection=redis.StrictRedis(host=machine.ip, port=6379, db=0, password=None))
            print("Connected to redis on {}, calling disktools.start_wipe on {}".format(machine.ip, target_device))

            job = q.enqueue_call('disktools.start_wipe', [target_device], timeout=86400)
            print("Job enqueued: {}".format(job))
            #sleep(5)

            #return render_template('machines/machine.html', results={machine})
            return redirect(url_for('MachinesView:get', uuid=uuid))  # Go back after starting.
        else:
            return "Not Found", 404

    def start_reboot(self, uuid):
        machine = Machine(uuid)
        if machine is not None:
            print("Attempting to start reboot on machine:")
            print(machine)
            print("Attempting to connect to redis on {}".format(machine.ip))

            # Redis queue connection setup so we can pass authentication
            q = Queue(connection=redis.StrictRedis(host=machine.ip, port=6379, db=0, password=None))
            print("Connected to redis on {}, calling disktools.start_reboot".format(machine.ip))

            job = q.enqueue_call('disktools.start_reboot', ["all"], timeout=86400)
            print("Job enqueued: {}".format(job))

            return redirect(url_for('MachinesView:get', uuid=uuid))  # Go back after starting.
        else:
            return "Not Found", 404

    def start_shutdown(self, uuid):
        machine = Machine(uuid)
        if machine is not None:
            print("Attempting to start shutdown on machine:")
            print(machine)
            print("Attempting to connect to redis on {}".format(machine.ip))

            # Redis queue connection setup so we can pass authentication
            q = Queue(connection=redis.StrictRedis(host=machine.ip, port=6379, db=0, password=None))
            print("Connected to redis on {}, calling disktools.start_shutdown".format(machine.ip))

            job = q.enqueue_call('disktools.start_shutdown', ["all"], timeout=86400)
            print("Job enqueued: {}".format(job))

            return redirect(url_for('MachinesView:get', uuid=uuid))  # Go back after starting.
        else:
            return "Not Found", 404
