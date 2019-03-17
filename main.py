#!/usr/local/bin/python3
"""AlayaNotes

Usage:
  main.py [run]
  main.py initdb
"""
from docopt import docopt
from passlib.hash import bcrypt
import subprocess
import os

from alayatodo import app, db
from alayatodo.models import Users


def _run_sql(filename):
    try:
        subprocess.check_output(
            "sqlite3 %s < %s" % (app.config['DATABASE'], filename),
            stderr=subprocess.STDOUT,
            shell=True
        )
    except subprocess.CalledProcessError as ex:
        print(ex)
        os._exit(1)


def encrypt_bd_passwords():
    users = Users.query.all()
    for user in users:
        db.session.query(Users).filter_by(id=user.id).update(
            {"password": bcrypt.hash(user.password)})
    db.session.commit()


def init_db():
    _run_sql('resources/database.sql')
    _run_sql('resources/fixtures.sql')
    _run_sql('resources/task_2_migration.sql')
    encrypt_bd_passwords()


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['initdb']:
        init_db()
        print("AlayaTodo: Database initialized.")
    else:
        app.run(use_reloader=True)
