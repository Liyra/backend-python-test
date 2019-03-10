#!/usr/local/bin/python3
"""AlayaNotes

Usage:
  main.py [run]
  main.py initdb
  main.py migrate_task_2
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
        db.session.query(Users).filter_by(id=user.id).update({ "password": bcrypt.hash(user.password)})
    db.session.commit()


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['initdb']:
        _run_sql('resources/database.sql')
        _run_sql('resources/fixtures.sql')
        encrypt_bd_passwords()
        print("AlayaTodo: Database initialized.")
    if args['migrate_task_2']:
        _run_sql('resources/task_2_migration.sql')
        print('AlayaTodo: Database migration for task 2 completed.')
    else:
        app.run(use_reloader=True)
