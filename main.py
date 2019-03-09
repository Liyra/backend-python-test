#!/usr/local/bin/python3
"""AlayaNotes

Usage:
  main.py [run]
  main.py initdb
  main.py migrate_task_2
"""
from docopt import docopt
import subprocess
import os

from alayatodo import app


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


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['initdb']:
        _run_sql('resources/database.sql')
        _run_sql('resources/fixtures.sql')
        print("AlayaTodo: Database initialized.")
    if args['migrate_task_2']:
        _run_sql('resources/task_2_migration.sql')
        print('AlayaTodo: Database migration for task 2 completed.')
    else:
        app.run(use_reloader=True)
